# LedgerLine — Money Movement with a Ledger You Can Prove

LedgerLine is a money movement application designed to ensure that financial transactions are accurate, authorised, traceable, and recorded consistently.

The project addresses common financial application risks such as duplicate transaction requests, simultaneous withdrawals, unauthorised access, incorrect account balances, and inconsistent transaction records.

**Challenge:** Snovasys Fresher Hiring Challenge 2026 — VVIT  
**Duration:** November 6–12, 2026  
**Repository:** [LedgerLine](https://github.com/Vasanthirangu2006/LedgerLine)

## Problem Statement

Financial applications must handle money movement reliably. Duplicate requests, concurrent transactions, unauthorised operations, and incorrect balance updates can result in financial losses.

LedgerLine addresses these challenges through transaction validation, idempotency, database transaction management, account ownership checks, and a traceable double-entry ledger.

## Technology Stack

| Component | Technology |
|---|---|
| Backend | Python, Flask |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Authentication | Flask-JWT-Extended |
| Frontend | TypeScript, Vite |
| HTTP Client | Axios |
| API Testing | Pytest, Flask Test Client |
| Version Control | Git and GitHub |

## Implemented Features

### 1. Authentication
- User registration and login.
- JWT-based authentication.
- Protected API endpoints.
- User profile retrieval.
- Password hashing.

### 2. Account Management
- Account creation.
- Retrieve user accounts.
- Retrieve account details.
- Check account balances.
- Account ownership validation.

### 3. Money Movement
- Deposits.
- Withdrawals.
- Account-to-account transfers.
- Positive amount and decimal precision validation.
- Prevention of withdrawals exceeding available balances.
- Currency compatibility validation.

### 4. Transaction Integrity
- Double-entry ledger records for transfers.
- Database transaction management.
- Account-level row locking during money movement.
- Consistent account balance and ledger updates.
- Idempotency key validation to prevent duplicate processing.
- Request fingerprinting to detect reuse of an idempotency key with a different payload.
- Concurrent withdrawal protection.

### 5. Audit and Transaction History
- Audit log creation for financial operations.
- Transaction history retrieval.
- Account-level access restrictions.
- Users can only view transactions and ledger entries associated with their own accounts.

### 6. Frontend
- Login and registration screens.
- Account overview and balance display.
- Deposit and withdrawal forms.
- Account-to-account transfer form.
- Transaction history.
- Backend API integration.
- Error and success notifications.

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
│   │   ├── conftest.py
│   │   ├── test_api.py
│   │   └── test_concurrency.py
│   ├── config.py
│   ├── requirements.txt
│   └── run.py
│
├── frontend/
│   ├── src/
│   │   ├── main.ts
│   │   └── style.css
│   ├── index.html
│   ├── package.json
│   └── vite.config.ts
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

- Python 3.10 or later.
- PostgreSQL.
- Node.js and npm.

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
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file inside the `backend/` directory.

```env
DB_USER=your_database_username
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ledgerline_db
JWT_SECRET_KEY=your_secure_random_secret
```

Replace the example values with your local PostgreSQL configuration. Never commit `.env` or expose database credentials.

### 5. Create the PostgreSQL database

Create a database named:

```sql
CREATE DATABASE ledgerline_db;
```

Ensure that the database user has the necessary permissions.

### 6. Start the Flask backend

```powershell
python run.py
```

Backend URL: `http://127.0.0.1:5001`

Health check: `http://127.0.0.1:5001/api/health`

## Frontend Setup

Open a separate terminal:

```powershell
cd LedgerLine/frontend
npm install
npm run dev
```

Frontend development URL: `http://127.0.0.1:5173`

The Vite development server proxies `/api` requests to the Flask backend running on port `5001`.

To create a production frontend build:

```powershell
npm run build
```

## API Overview

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

Financial transaction requests require an idempotency key supplied through the `Idempotency-Key` request header.

Refer to [docs/API.md](docs/API.md) for additional API details.

## Verification and Testing

The project was tested through both manual API/database verification and automated backend tests.

### Automated Test Results

Run the test suite from the `backend/` directory:

```powershell
python -m pytest -v
```

**Latest result: 15 passed in 15.27 seconds.**

Automated tests cover:

- User registration, login, and profile retrieval.
- Duplicate registration and invalid login rejection.
- Protected endpoint authentication.
- Account ownership restrictions.
- Deposit processing and idempotent retries.
- Rejection of reused idempotency keys with different request payloads.
- Invalid transaction amount validation.
- Insufficient balance rejection.
- Transfer ledger debit-credit verification.
- User-specific transaction history.
- Simultaneous withdrawal protection.

### Concurrency Verification

A dedicated concurrency test sends two simultaneous ₹80 withdrawal requests against an account with ₹100.

Expected and verified result:

- One withdrawal succeeds.
- The other withdrawal is rejected.
- Final account balance remains ₹20.
- The account balance does not become negative.

This verifies the tested concurrent withdrawal scenario; it is not a full-scale load or stress test.

### Manual Verification

The following scenarios were also manually verified using API requests, the frontend, and PostgreSQL queries:

- Successful deposits, withdrawals, and transfers.
- Exact-request retries.
- Duplicate request protection.
- Rejection of insufficient-balance withdrawals.
- Transaction history access restrictions.
- Account balance reconciliation against ledger entries.
- Double-entry debit-credit verification.

## Current Development Status

**Completed**
- Flask backend and PostgreSQL integration.
- JWT authentication and account management.
- Deposits, withdrawals, and transfers.
- Double-entry ledger and audit logging.
- Idempotency handling.
- Database transaction and account locking logic.
- Integrated TypeScript frontend.
- Automated backend tests: 15 passing.
- Manual API, frontend, and database verification.
- Concurrent withdrawal scenario testing.

**Further improvements**
- Broader automated security and concurrency testing.
- Production deployment and configuration.
- Additional monitoring and operational safeguards.

## AI Tools Used

ChatGPT (OpenAI) was used as a development assistant for project planning, implementation guidance, debugging, database configuration, API development, testing guidance, and Git/GitHub workflows.

Implementation decisions and generated code were reviewed and tested during development. Testing results are reported only for scenarios that were actually executed.

## Repository

GitHub: https://github.com/Vasanthirangu2006/LedgerLine

---

**LedgerLine — Every transaction should be accurate, authorised, and traceable.**