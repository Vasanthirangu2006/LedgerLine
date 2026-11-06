
import hashlib
import json
import uuid

from decimal import Decimal, InvalidOperation

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import (
    Account,
    Transaction,
    LedgerEntry,
    IdempotencyKey,
    AuditLog
)


transactions_bp = Blueprint(
    "transactions",
    __name__,
    url_prefix="/api/transactions"
)


# --------------------------------------------------
# 1. AMOUNT VALIDATION
# --------------------------------------------------

def validate_amount(value):

    try:
        amount = Decimal(str(value))

        if not amount.is_finite():
            return None

        if amount <= 0:
            return None

        if amount > Decimal("9999999999999.99"):
            return None

        if amount.as_tuple().exponent < -2:
            return None

        return amount.quantize(Decimal("0.01"))

    except (InvalidOperation, ValueError, TypeError):
        return None


# --------------------------------------------------
# 2. IDEMPOTENCY CHECK
# --------------------------------------------------

def check_idempotency(user_id):

    key = request.headers.get("Idempotency-Key")

    if not key:
        return None, None, (jsonify({
            "error": "Idempotency-Key header is required"
        }), 400)

    if len(key) > 100:
        return None, None, (jsonify({
            "error": "Idempotency key must not exceed 100 characters"
        }), 400)

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return None, None, (jsonify({
            "error": "Request body must be a valid JSON object"
        }), 400)

    fingerprint_data = (
        request.method
        + ":"
        + request.path
        + ":"
        + json.dumps(data, sort_keys=True, separators=(",", ":"))
    )

    request_hash = hashlib.sha256(
        fingerprint_data.encode("utf-8")
    ).hexdigest()

    existing = IdempotencyKey.query.filter_by(key=key).first()

    if existing:

        if existing.user_id != user_id:
            return None, None, (jsonify({
                "error": "This idempotency key belongs to another user"
            }), 409)

        if not existing.request_hash:
            return None, None, (jsonify({
                "error": "Legacy idempotency key. Use a new key"
            }), 409)

        if existing.request_hash != request_hash:
            return None, None, (jsonify({
                "error": "Idempotency key was already used with a different request"
            }), 409)

        if existing.response:
            return None, None, (jsonify(existing.response), 201)

        return None, None, (jsonify({
            "error": "Request with this idempotency key is still processing"
        }), 409)

    return key, request_hash, None


# --------------------------------------------------
# 3. HANDLE CONCURRENT IDEMPOTENCY REQUESTS
# --------------------------------------------------

def handle_idempotency_conflict(key, user_id, request_hash):

    existing = IdempotencyKey.query.filter_by(key=key).first()

    if existing:

        if existing.user_id != user_id:
            return jsonify({
                "error": "This idempotency key belongs to another user"
            }), 409

        if not existing.request_hash:
            return jsonify({
                "error": "Legacy idempotency key. Use a new key"
            }), 409

        if existing.request_hash != request_hash:
            return jsonify({
                "error": "Idempotency key was already used with a different request"
            }), 409

        if existing.response:
            return jsonify(existing.response), 201

    return None


# --------------------------------------------------
# 4. CREATE TRANSACTION REFERENCE
# --------------------------------------------------

def generate_reference():

    return "TXN-" + uuid.uuid4().hex[:20].upper()


# --------------------------------------------------
# 5. SAVE AUDIT LOG
# --------------------------------------------------

def create_audit_log(user_id, action, details):

    audit = AuditLog(
        user_id=user_id,
        action=action,
        details=details
    )

    db.session.add(audit)


# --------------------------------------------------
# 6. DEPOSIT
# --------------------------------------------------

@transactions_bp.route("/deposit", methods=["POST"])
@jwt_required()
def deposit():

    current_user_id = int(get_jwt_identity())

    idempotency_key, request_hash, replay = check_idempotency(
        current_user_id
    )

    if replay:
        return replay

    data = request.get_json()

    account_id = data.get("account_id")
    amount = validate_amount(data.get("amount"))
    description = data.get("description", "Deposit")

    if amount is None:
        return jsonify({
            "error": "Invalid amount"
        }), 400

    if not account_id:
        return jsonify({
            "error": "account_id is required"
        }), 400

    try:

        account = Account.query.filter_by(
            id=account_id,
            user_id=current_user_id
        ).with_for_update().first()

        if not account:
            return jsonify({
                "error": "Account not found"
            }), 404

        if account.status != "active":
            return jsonify({
                "error": "Account is not active"
            }), 400

        idempotency_record = IdempotencyKey(
            key=idempotency_key,
            user_id=current_user_id,
            request_hash=request_hash,
            response={}
        )

        db.session.add(idempotency_record)

        transaction = Transaction(
            reference_id=generate_reference(),
            transaction_type="deposit",
            amount=amount,
            status="completed",
            description=description
        )

        db.session.add(transaction)
        db.session.flush()

        account.balance += amount

        ledger_entry = LedgerEntry(
            transaction_id=transaction.id,
            account_id=account.id,
            entry_type="credit",
            amount=amount
        )

        db.session.add(ledger_entry)

        create_audit_log(
            current_user_id,
            "DEPOSIT",
            {
                "transaction_id": transaction.id,
                "account_id": account.id,
                "amount": str(amount)
            }
        )

        response_data = {
            "message": "Deposit successful",
            "account": {
                "account_id": account.id,
                "account_number": account.account_number,
                "balance": str(account.balance),
                "currency": account.currency
            },
            "transaction": {
                "transaction_id": transaction.id,
                "reference_id": transaction.reference_id,
                "amount": str(amount),
                "status": transaction.status
            }
        }

        idempotency_record.response = response_data

        db.session.commit()

        return jsonify(response_data), 201

    except IntegrityError:

        db.session.rollback()

        replay = handle_idempotency_conflict(
            idempotency_key,
            current_user_id,
            request_hash
        )

        if replay:
            return replay

        return jsonify({
            "error": "Database integrity error"
        }), 409

    except Exception as e:

        db.session.rollback()

        return jsonify({
            "error": "Deposit failed",
            "details": str(e)
        }), 500


# --------------------------------------------------
# 7. WITHDRAWAL
# --------------------------------------------------

@transactions_bp.route("/withdraw", methods=["POST"])
@jwt_required()
def withdraw():

    current_user_id = int(get_jwt_identity())

    idempotency_key, request_hash, replay = check_idempotency(
        current_user_id
    )

    if replay:
        return replay

    data = request.get_json()

    account_id = data.get("account_id")
    amount = validate_amount(data.get("amount"))
    description = data.get("description", "Withdrawal")

    if amount is None:
        return jsonify({
            "error": "Invalid amount"
        }), 400

    if not account_id:
        return jsonify({
            "error": "account_id is required"
        }), 400

    try:

        account = Account.query.filter_by(
            id=account_id,
            user_id=current_user_id
        ).with_for_update().first()

        if not account:
            return jsonify({
                "error": "Account not found"
            }), 404

        if account.status != "active":
            return jsonify({
                "error": "Account is not active"
            }), 400

        if account.balance < amount:
            return jsonify({
                "error": "Insufficient balance"
            }), 400

        idempotency_record = IdempotencyKey(
            key=idempotency_key,
            user_id=current_user_id,
            request_hash=request_hash,
            response={}
        )

        db.session.add(idempotency_record)

        transaction = Transaction(
            reference_id=generate_reference(),
            transaction_type="withdrawal",
            amount=amount,
            status="completed",
            description=description
        )

        db.session.add(transaction)
        db.session.flush()

        account.balance -= amount

        ledger_entry = LedgerEntry(
            transaction_id=transaction.id,
            account_id=account.id,
            entry_type="debit",
            amount=amount
        )

        db.session.add(ledger_entry)

        create_audit_log(
            current_user_id,
            "WITHDRAWAL",
            {
                "transaction_id": transaction.id,
                "account_id": account.id,
                "amount": str(amount)
            }
        )

        response_data = {
            "message": "Withdrawal successful",
            "account": {
                "account_id": account.id,
                "account_number": account.account_number,
                "balance": str(account.balance),
                "currency": account.currency
            },
            "transaction": {
                "transaction_id": transaction.id,
                "reference_id": transaction.reference_id,
                "amount": str(amount),
                "status": transaction.status
            }
        }

        idempotency_record.response = response_data

        db.session.commit()

        return jsonify(response_data), 201

    except IntegrityError:

        db.session.rollback()

        replay = handle_idempotency_conflict(
            idempotency_key,
            current_user_id,
            request_hash
        )

        if replay:
            return replay

        return jsonify({
            "error": "Database integrity error"
        }), 409

    except Exception as e:

        db.session.rollback()

        return jsonify({
            "error": "Withdrawal failed",
            "details": str(e)
        }), 500


# --------------------------------------------------
# 8. TRANSFER
# --------------------------------------------------

@transactions_bp.route("/transfer", methods=["POST"])
@jwt_required()
def transfer():

    current_user_id = int(get_jwt_identity())

    idempotency_key, request_hash, replay = check_idempotency(
        current_user_id
    )

    if replay:
        return replay

    data = request.get_json()

    sender_account_id = data.get("sender_account_id")
    receiver_account_id = data.get("receiver_account_id")
    amount = validate_amount(data.get("amount"))
    description = data.get("description", "Money transfer")

    if amount is None:
        return jsonify({
            "error": "Invalid amount"
        }), 400

    if not sender_account_id or not receiver_account_id:
        return jsonify({
            "error": "Sender and receiver account IDs are required"
        }), 400

    if sender_account_id == receiver_account_id:
        return jsonify({
            "error": "Cannot transfer money to the same account"
        }), 400

    try:

        account_ids = sorted([
            sender_account_id,
            receiver_account_id
        ])

        locked_accounts = Account.query.filter(
            Account.id.in_(account_ids)
        ).order_by(Account.id).with_for_update().all()

        accounts = {
            account.id: account
            for account in locked_accounts
        }

        sender = accounts.get(sender_account_id)
        receiver = accounts.get(receiver_account_id)

        if not sender or sender.user_id != current_user_id:
            return jsonify({
                "error": "Sender account not found"
            }), 404

        if not receiver:
            return jsonify({
                "error": "Receiver account not found"
            }), 404

        if sender.status != "active" or receiver.status != "active":
            return jsonify({
                "error": "Both accounts must be active"
            }), 400

        if sender.currency != receiver.currency:
            return jsonify({
                "error": "Currency mismatch between accounts"
            }), 400

        if sender.balance < amount:
            return jsonify({
                "error": "Insufficient balance"
            }), 400

        idempotency_record = IdempotencyKey(
            key=idempotency_key,
            user_id=current_user_id,
            request_hash=request_hash,
            response={}
        )

        db.session.add(idempotency_record)

        transaction = Transaction(
            reference_id=generate_reference(),
            transaction_type="transfer",
            amount=amount,
            status="completed",
            description=description
        )

        db.session.add(transaction)
        db.session.flush()

        sender.balance -= amount
        receiver.balance += amount

        sender_entry = LedgerEntry(
            transaction_id=transaction.id,
            account_id=sender.id,
            entry_type="debit",
            amount=amount
        )

        receiver_entry = LedgerEntry(
            transaction_id=transaction.id,
            account_id=receiver.id,
            entry_type="credit",
            amount=amount
        )

        db.session.add(sender_entry)
        db.session.add(receiver_entry)

        create_audit_log(
            current_user_id,
            "TRANSFER",
            {
                "transaction_id": transaction.id,
                "sender_account_id": sender.id,
                "receiver_account_id": receiver.id,
                "amount": str(amount)
            }
        )

        response_data = {
            "message": "Transfer successful",
            "sender_account": {
                "account_id": sender.id,
                "account_number": sender.account_number,
                "balance": str(sender.balance)
            },
            "receiver_account": {
                "account_id": receiver.id,
                "account_number": receiver.account_number,
                "balance": str(receiver.balance)
            },
            "transaction": {
                "transaction_id": transaction.id,
                "reference_id": transaction.reference_id,
                "amount": str(amount),
                "status": transaction.status
            }
        }

        idempotency_record.response = response_data

        db.session.commit()

        return jsonify(response_data), 201

    except IntegrityError:

        db.session.rollback()

        replay = handle_idempotency_conflict(
            idempotency_key,
            current_user_id,
            request_hash
        )

        if replay:
            return replay

        return jsonify({
            "error": "Database integrity error"
        }), 409

    except Exception as e:

        db.session.rollback()

        return jsonify({
            "error": "Transfer failed",
            "details": str(e)
        }), 500


# --------------------------------------------------
# 9. TRANSACTION HISTORY
# --------------------------------------------------

@transactions_bp.route("/", methods=["GET"])
@jwt_required()
def get_transactions():

    current_user_id = int(get_jwt_identity())

    try:

        transactions = (
            Transaction.query
            .join(
                LedgerEntry,
                LedgerEntry.transaction_id == Transaction.id
            )
            .join(
                Account,
                Account.id == LedgerEntry.account_id
            )
            .filter(Account.user_id == current_user_id)
            .distinct()
            .order_by(Transaction.created_at.desc())
            .limit(50)
            .all()
        )

        result = []

        for transaction in transactions:

            entries = (
                db.session.query(LedgerEntry)
                .join(
                    Account,
                    Account.id == LedgerEntry.account_id
                )
                .filter(
                    LedgerEntry.transaction_id == transaction.id,
                    Account.user_id == current_user_id
                )
                .all()
            )

            result.append({
                "transaction_id": transaction.id,
                "reference_id": transaction.reference_id,
                "transaction_type": transaction.transaction_type,
                "amount": str(transaction.amount),
                "status": transaction.status,
                "description": transaction.description,
                "created_at": transaction.created_at.isoformat(),
                "entries": [
                    {
                        "account_id": entry.account_id,
                        "entry_type": entry.entry_type,
                        "amount": str(entry.amount)
                    }
                    for entry in entries
                ]
            })

        return jsonify({
            "count": len(result),
            "transactions": result
        }), 200

    except Exception as e:

        return jsonify({
            "error": "Could not retrieve transactions",
            "details": str(e)
        }), 500
