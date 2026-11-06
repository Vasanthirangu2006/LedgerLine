# LedgerLine — Money Movement with a Ledger You Can Prove

LedgerLine is a secure money movement backend designed to ensure that financial transactions are accurate, authorised, traceable, and recorded consistently.

The project addresses common financial application risks such as duplicate transaction requests, simultaneous withdrawals, unauthorised access, incorrect account balances, and inconsistent transaction records.

**Challenge:** Snovasys Fresher Hiring Challenge 2026 — VVIT  
**Duration:** November 6–12, 2026  
**Repository:** LedgerLine

## Problem Statement

Financial applications must handle money movement reliably. Duplicate requests, concurrent transactions, unauthorised operations, and incorrect balance updates can result in financial losses.

LedgerLine aims to address these challenges through transaction validation, idempotency, database transaction management, account ownership checks, and a traceable double-entry ledger.

## Technology Stack

| Component | Technology |
|---|---|
| Backend | Python, Flask |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Authentication | Flask-JWT-Extended |
| Frontend | React / Vite |
| API Testing | Postman |
| Version Control | Git and GitHub |

## Implemented Features

### Authentication
- User registration and login.
- JWT-based authentication.
- Protected API endpoints.
- User profile retrieval.

### Account Management
- Account creation.
- Retrieve user accounts.
- Retrieve account details.
- Check account balances.
- Account ownership validation.

### Money Movement
- Deposits.
- Withdrawals.
- Account-to-account transfers.
- Positive amount and decimal precision validation.
- Prevention of withdrawals exceeding available balances.
- Currency compatibility validation.

### Transaction Integrity
- Double-entry ledger records for transfers.
- Database transaction management.
- Account-level locking during money movement.
- Consistent account balance and ledger updates.
- Idempotency key validation to prevent duplicate processing.
- Request fingerprinting to detect reuse of an idempotency key with a different payload.

### Audit and Transaction History
- Audit log creation for financial operations.
- Transaction history retrieval.
- Account-level access restrictions.
- Users can only view transactions and ledger entries associated with their own accounts.

## Project Structure

```text
LedgerLine/
│
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   │   ├── auth.py
│   │   │   ├── accounts.py
│   │   │   └── transactions.py
│   │   ├── models.py
│   │   └── __init__.py
│   │
│   ├── tests/
│   ├── config.py
│   ├── requirements.txt
│   └── run.py
│
├── frontend/
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── package-lock.json
│
├── docs/
│   └── API.md
│
├── .gitignore
├── README.md
├── PROMPTS.md
└── THREATS.md
```

## Prerequisites

Install the following before running the project:

- Python 3.10 or later (use a version compatible with the installed dependencies).
- PostgreSQL.
- Node.js and npm (for the frontend).

## Backend Setup

### 1. Clone the repository

```bash
git clone https://github.com/Vasanthirangu2006/LedgerLine.git
cd LedgerLine
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file inside the `backend/` directory.

Add your local PostgreSQL configuration:

```env
DB_USER=your_database_username
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ledgerline_db
JWT_SECRET_KEY=your_secure_random_secret
```

Replace the example values with your own local configuration. Never commit `.env` or expose database credentials.

### 5. Create the PostgreSQL database

Create a PostgreSQL database named:

```sql
CREATE DATABASE ledgerline_db;
```

Ensure that the database user has the necessary permissions.

### 6. Start the Flask backend

```powershell
python run.py
```

Backend URL:

`http://127.0.0.1:5001`

Health check:

`http://127.0.0.1:5001/api/health`

## Frontend Setup

The React/Vite frontend project is included in the repository.

To install its dependencies:

```powershell
cd frontend
npm install
npm run dev
```

Frontend development URL:

`http://localhost:5173`

The frontend is currently a scaffold and is not yet a complete integrated financial dashboard.

## API Overview

The backend provides endpoints for authentication, account management, and financial transactions.

| Module | Endpoint | Method |
|---|---|---|
| Authentication | `/api/auth/register` | POST |
| Authentication | `/api/auth/login` | POST |
| Authentication | `/api/auth/profile` | GET |
| Accounts | `/api/accounts/` | POST |
| Accounts | `/api/accounts/` | GET |
| Accounts | `/api/accounts/<account_id>` | GET |
| Accounts | `/api/accounts/<account_id>/balance` | GET |
| Transactions | `/api/transactions/deposit` | POST |
| Transactions | `/api/transactions/withdraw` | POST |
| Transactions | `/api/transactions/transfer` | POST |
| Transactions | `/api/transactions/` | GET |

Protected endpoints require a valid JWT access token.

For financial transaction requests, an idempotency key should be supplied using the `Idempotency-Key` request header.

Refer to [docs/API.md](docs/API.md) for additional API details.

## Verification and Testing

The following backend scenarios were manually verified using API requests and PostgreSQL database queries:

- Successful deposit and exact-request retry.
- Successful withdrawal and exact-request retry.
- Successful transfer and exact-request retry.
- Rejection of a reused idempotency key with a different request payload.
- Transaction history access for different users.
- Account ownership and ledger-entry visibility checks.
- Account balance reconciliation against ledger entries.
- Double-entry verification for transfers.

### Sample verification results

| Verification | Result |
|---|---|
| Deposit and retry | Passed |
| Withdrawal and retry | Passed |
| Transfer and retry | Passed |
| Duplicate request protection | Passed |
| Transaction history access checks | Passed |
| Account balance reconciliation | Passed |
| Transfer debit-credit verification | Passed |

These results represent the scenarios manually tested during development. They do not represent a complete automated security or concurrency test suite.

## Current Development Status

**Completed:**
- Flask backend setup.
- PostgreSQL database integration.
- JWT authentication.
- Account management.
- Deposits, withdrawals, and transfers.
- Double-entry ledger.
- Idempotency handling.
- Transaction history and audit logging.
- Manual backend verification.

**Remaining work:**
- Complete React frontend dashboard.
- Integrate frontend with backend APIs.
- Add comprehensive automated tests.
- Perform dedicated concurrent transaction and security testing.
- Deployment and production configuration.
- Prepare a complete demonstration.

## AI Tools Used

ChatGPT (OpenAI) was used as a development assistant for project planning, implementation guidance, debugging, database configuration, API development, and Git/GitHub workflows.

All implementation decisions and generated code were reviewed and tested during development. Testing results are reported only for scenarios that were actually executed.

## Repository

GitHub: https://github.com/Vasanthirangu2006/LedgerLine

---

**LedgerLine — Every transaction should be accurate, authorised, and traceable.**