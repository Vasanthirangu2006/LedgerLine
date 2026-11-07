
import pytest

from app import db
from app.models import Account, Transaction, LedgerEntry


def register_user(client, email):
    return client.post(
        "/api/auth/register",
        json={
            "name": "Test User",
            "email": email,
            "password": "TestPass@123"
        }
    )


def login_user(client, email):
    response = client.post(
        "/api/auth/login",
        json={
            "email": email,
            "password": "TestPass@123"
        }
    )

    assert response.status_code == 200

    token = response.get_json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


def create_account(client, headers):
    response = client.post(
        "/api/accounts/",
        json={},
        headers=headers
    )

    assert response.status_code == 201

    return response.get_json()["account"]["id"]


def test_register_login_and_profile(client):
    response = register_user(client, "user1@test.com")

    assert response.status_code == 201

    headers = login_user(client, "user1@test.com")

    profile = client.get(
        "/api/auth/profile",
        headers=headers
    )

    assert profile.status_code == 200
    assert profile.get_json()["email"] == "user1@test.com"


def test_duplicate_registration_is_rejected(client):
    register_user(client, "duplicate@test.com")

    response = register_user(client, "duplicate@test.com")

    assert response.status_code == 409


def test_invalid_login_is_rejected(client):
    register_user(client, "login@test.com")

    response = client.post(
        "/api/auth/login",
        json={
            "email": "login@test.com",
            "password": "WrongPassword"
        }
    )

    assert response.status_code == 401


def test_protected_profile_requires_authentication(client):
    response = client.get("/api/auth/profile")

    assert response.status_code == 401


def test_user_cannot_access_another_users_account(client):
    register_user(client, "owner@test.com")
    owner_headers = login_user(client, "owner@test.com")
    account_id = create_account(client, owner_headers)

    register_user(client, "outsider@test.com")
    outsider_headers = login_user(client, "outsider@test.com")

    response = client.get(
        f"/api/accounts/{account_id}",
        headers=outsider_headers
    )

    assert response.status_code == 404


def test_deposit_and_idempotent_retry(client):
    register_user(client, "deposit@test.com")
    headers = login_user(client, "deposit@test.com")
    account_id = create_account(client, headers)

    payload = {
        "account_id": account_id,
        "amount": "50.00"
    }

    headers_with_key = {
        **headers,
        "Idempotency-Key": "deposit-test-001"
    }

    first = client.post(
        "/api/transactions/deposit",
        json=payload,
        headers=headers_with_key
    )

    second = client.post(
        "/api/transactions/deposit",
        json=payload,
        headers=headers_with_key
    )

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.get_json() == second.get_json()

    balance = client.get(
        f"/api/accounts/{account_id}/balance",
        headers=headers
    )

    assert balance.get_json()["balance"] == "50.00"


def test_same_idempotency_key_cannot_be_reused_for_different_request(client):
    register_user(client, "key@test.com")
    headers = login_user(client, "key@test.com")
    account_id = create_account(client, headers)

    request_headers = {
        **headers,
        "Idempotency-Key": "deposit-test-002"
    }

    first = client.post(
        "/api/transactions/deposit",
        json={"account_id": account_id, "amount": "50"},
        headers=request_headers
    )

    second = client.post(
        "/api/transactions/deposit",
        json={"account_id": account_id, "amount": "60"},
        headers=request_headers
    )

    assert first.status_code == 201
    assert second.status_code == 409


@pytest.mark.parametrize(
    "amount",
    ["0", "-10", "1.234", "invalid"]
)
def test_invalid_deposit_amounts_are_rejected(client, amount):
    register_user(client, "amount@test.com")
    headers = login_user(client, "amount@test.com")
    account_id = create_account(client, headers)

    response = client.post(
        "/api/transactions/deposit",
        json={
            "account_id": account_id,
            "amount": amount
        },
        headers={
            **headers,
            "Idempotency-Key": f"invalid-{amount}"
        }
    )

    assert response.status_code == 400


def test_withdrawal_rejects_insufficient_balance(client):
    register_user(client, "withdraw@test.com")
    headers = login_user(client, "withdraw@test.com")
    account_id = create_account(client, headers)

    response = client.post(
        "/api/transactions/withdraw",
        json={
            "account_id": account_id,
            "amount": "100"
        },
        headers={
            **headers,
            "Idempotency-Key": "withdraw-test-001"
        }
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Insufficient balance"

    balance = client.get(
        f"/api/accounts/{account_id}/balance",
        headers=headers
    )

    assert balance.get_json()["balance"] == "0.00"


def test_transfer_creates_balanced_ledger_entries(client, app):
    register_user(client, "sender@test.com")
    sender_headers = login_user(client, "sender@test.com")
    sender_id = create_account(client, sender_headers)

    register_user(client, "receiver@test.com")
    receiver_headers = login_user(client, "receiver@test.com")
    receiver_id = create_account(client, receiver_headers)

    deposit = client.post(
        "/api/transactions/deposit",
        json={
            "account_id": sender_id,
            "amount": "100"
        },
        headers={
            **sender_headers,
            "Idempotency-Key": "transfer-funding-001"
        }
    )

    assert deposit.status_code == 201

    transfer = client.post(
        "/api/transactions/transfer",
        json={
            "sender_account_id": sender_id,
            "receiver_account_id": receiver_id,
            "amount": "30"
        },
        headers={
            **sender_headers,
            "Idempotency-Key": "transfer-test-001"
        }
    )

    assert transfer.status_code == 201

    sender_balance = client.get(
        f"/api/accounts/{sender_id}/balance",
        headers=sender_headers
    ).get_json()["balance"]

    receiver_balance = client.get(
        f"/api/accounts/{receiver_id}/balance",
        headers=receiver_headers
    ).get_json()["balance"]

    assert sender_balance == "70.00"
    assert receiver_balance == "30.00"

    with app.app_context():
        transaction = Transaction.query.filter_by(
            transaction_type="transfer"
        ).one()

        entries = LedgerEntry.query.filter_by(
            transaction_id=transaction.id
        ).all()

        assert len(entries) == 2

        debit = next(
            entry for entry in entries
            if entry.entry_type == "debit"
        )

        credit = next(
            entry for entry in entries
            if entry.entry_type == "credit"
        )

        assert debit.amount == credit.amount
        assert debit.amount == transaction.amount
        assert debit.account_id == sender_id
        assert credit.account_id == receiver_id


def test_transaction_history_only_shows_users_own_entries(client):
    register_user(client, "history-sender@test.com")
    sender_headers = login_user(
        client, "history-sender@test.com"
    )
    sender_id = create_account(client, sender_headers)

    register_user(client, "history-receiver@test.com")
    receiver_headers = login_user(
        client, "history-receiver@test.com"
    )
    receiver_id = create_account(client, receiver_headers)

    client.post(
        "/api/transactions/deposit",
        json={"account_id": sender_id, "amount": "100"},
        headers={
            **sender_headers,
            "Idempotency-Key": "history-deposit-001"
        }
    )

    transfer = client.post(
        "/api/transactions/transfer",
        json={
            "sender_account_id": sender_id,
            "receiver_account_id": receiver_id,
            "amount": "25"
        },
        headers={
            **sender_headers,
            "Idempotency-Key": "history-transfer-001"
        }
    )

    assert transfer.status_code == 201

    sender_history = client.get(
        "/api/transactions/",
        headers=sender_headers
    ).get_json()

    receiver_history = client.get(
        "/api/transactions/",
        headers=receiver_headers
    ).get_json()

    assert sender_history["count"] == 2
    assert receiver_history["count"] == 1

    receiver_transfer = receiver_history["transactions"][0]

    assert all(
        entry["account_id"] == receiver_id
        for entry in receiver_transfer["entries"]
    )
