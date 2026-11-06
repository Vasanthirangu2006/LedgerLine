
import secrets

from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models import User, Account


accounts_bp = Blueprint(
    "accounts", __name__, url_prefix="/api/accounts"
)


def generate_account_number():
    while True:
        number = "LL" + "".join(
            secrets.choice("0123456789") for _ in range(12)
        )

        existing = Account.query.filter_by(
            account_number=number
        ).first()

        if not existing:
            return number


# 1. CREATE BANK ACCOUNT
@accounts_bp.route("/", methods=["POST"])
@jwt_required()
def create_account():

    user_id = int(get_jwt_identity())

    user = db.session.get(User, user_id)

    if not user:
        return {"error": "User not found"}, 404

    account_number = generate_account_number()

    account = Account(
        account_number=account_number,
        user_id=user_id,
        account_type="savings",
        balance=0,
        currency="INR",
        status="active"
    )

    try:
        db.session.add(account)
        db.session.commit()

    except Exception:
        db.session.rollback()
        return {"error": "Unable to create account"}, 500

    return {
        "message": "Bank account created successfully",
        "account": {
            "id": account.id,
            "account_number": account.account_number,
            "account_type": account.account_type,
            "balance": str(account.balance),
            "currency": account.currency,
            "status": account.status
        }
    }, 201


# 2. VIEW ALL USER ACCOUNTS
@accounts_bp.route("/", methods=["GET"])
@jwt_required()
def get_accounts():

    user_id = int(get_jwt_identity())

    accounts = Account.query.filter_by(
        user_id=user_id
    ).all()

    return {
        "accounts": [
            {
                "id": account.id,
                "account_number": account.account_number,
                "account_type": account.account_type,
                "balance": str(account.balance),
                "currency": account.currency,
                "status": account.status
            }
            for account in accounts
        ]
    }, 200


# 3. VIEW PARTICULAR ACCOUNT
@accounts_bp.route("/<int:account_id>", methods=["GET"])
@jwt_required()
def get_account(account_id):

    user_id = int(get_jwt_identity())

    account = Account.query.filter_by(
        id=account_id,
        user_id=user_id
    ).first()

    if not account:
        return {"error": "Account not found"}, 404

    return {
        "account": {
            "id": account.id,
            "account_number": account.account_number,
            "account_type": account.account_type,
            "balance": str(account.balance),
            "currency": account.currency,
            "status": account.status
        }
    }, 200


# 4. CHECK ACCOUNT BALANCE
@accounts_bp.route(
    "/<int:account_id>/balance", methods=["GET"]
)
@jwt_required()
def check_balance(account_id):

    user_id = int(get_jwt_identity())

    account = Account.query.filter_by(
        id=account_id,
        user_id=user_id
    ).first()

    if not account:
        return {"error": "Account not found"}, 404

    return {
        "account_number": account.account_number,
        "balance": str(account.balance),
        "currency": account.currency
    }, 200
