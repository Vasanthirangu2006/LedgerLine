
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from app import db
from app.models import Account


def test_simultaneous_withdrawals_cannot_overdraw(app):
    # Prepare a fresh account with ₹100.
    with app.app_context():
        from app.models import User
        from werkzeug.security import generate_password_hash

        user = User(
            name="Concurrency Test",
            email="concurrency@test.com",
            password_hash=generate_password_hash("TestPass@123"),
            role="customer"
        )

        db.session.add(user)
        db.session.flush()

        account = Account(
            account_number="LL999999999999",
            user_id=user.id,
            account_type="savings",
            balance=100,
            currency="INR",
            status="active"
        )

        db.session.add(account)
        db.session.commit()

        account_id = account.id

    # Create a JWT token for the test user.
    with app.test_client() as client:
        login = client.post(
            "/api/auth/login",
            json={
                "email": "concurrency@test.com",
                "password": "TestPass@123"
            }
        )

        assert login.status_code == 200
        token = login.get_json()["access_token"]

    barrier = Barrier(2)

    def withdraw(amount, key):
        # Each worker gets its own Flask test client and request context.
        with app.test_client() as client:
            barrier.wait(timeout=10)

            return client.post(
                "/api/transactions/withdraw",
                json={
                    "account_id": account_id,
                    "amount": str(amount)
                },
                headers={
                    "Authorization": f"Bearer {token}",
                    "Idempotency-Key": key
                }
            )

    # Both requests attempt to withdraw ₹80 at nearly the same time.
    with ThreadPoolExecutor(max_workers=2) as executor:
        future_one = executor.submit(
            withdraw, 80, "concurrent-withdrawal-001"
        )
        future_two = executor.submit(
            withdraw, 80, "concurrent-withdrawal-002"
        )

        response_one = future_one.result(timeout=30)
        response_two = future_two.result(timeout=30)

    statuses = [
        response_one.status_code,
        response_two.status_code
    ]

    # Exactly one withdrawal must succeed.
    assert statuses.count(201) == 1

    # The other withdrawal must be rejected.
    assert statuses.count(400) == 1

    # Verify the final database balance.
    with app.app_context():
        db.session.expire_all()

        final_account = db.session.get(Account, account_id)

        assert str(final_account.balance) == "20.00"
        assert final_account.balance >= 0
