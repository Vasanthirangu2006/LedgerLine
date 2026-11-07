# LedgerLine — Money Movement with a Ledger You Can Prove

LedgerLine is a digital banking simulation designed to make financial transactions accurate, authorized, traceable, and consistent.

The application addresses common financial system risks such as duplicate transaction requests, simultaneous withdrawals, unauthorized access, incorrect account balances, and inconsistent transaction records.

**Challenge:** Snovasys Fresher Hiring Challenge 2026 — VVIT  
**Duration:** November 6–12, 2026

## Live Application

- **Frontend:** https://ledgerline-beta-eight.vercel.app
- **Backend API:** https://ledgerline-backend-y824.onrender.com
- **Backend Health:** https://ledgerline-backend-y824.onrender.com/api/health
- **Database Health:** https://ledgerline-backend-y824.onrender.com/api/db-check

The application uses a deployed Flask backend, PostgreSQL database, and Vite frontend.

## Project Demo

Watch the LedgerLine application walkthrough:

[▶ Watch LedgerLine Demo Video](https://drive.google.com/file/d/1HRnI21VtgcHzQto12lSWnrEe9TDhqRng/view?usp=sharing)

## Problem Statement

Financial applications must process money movements reliably. Duplicate requests, concurrent transactions, unauthorized operations, and incorrect balance updates can result in financial losses.

LedgerLine addresses these challenges through:

- Transaction validation.
- Idempotency handling.
- Database transaction management.
- Account ownership checks.
- Ledger records and audit logging.
- Concurrent withdrawal protection.

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
| Backend Hosting | Render |
| Database Hosting | Neon PostgreSQL |
| Frontend Hosting | Vercel |
| Version Control | Git and GitHub |

## Implemented Features

### 1. Authentication

- User registration and login.
- JWT-based authentication.
- Protected API endpoints.
- User profile retrieval.
- Password hashing.

### 2. Account Management

- Bank account creation.
- Retrieve user accounts.
- Retrieve individual account details.
- Check account balances.
- Account ownership validation.
- Support for savings and current account types.

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
- Users can only access transaction and ledger information associated with their own accounts.

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
│   │
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
├── README.md
├── PROMPTS.md
├── THREATS.md
└── .gitignore
```

## Prerequisites

- Python 3.10 or later.
- PostgreSQL.
- Node.js and npm.
- Git.

## Local Installation and Setup

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

### 3. Install backend dependencies

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

Replace the example values with your local PostgreSQL configuration.

Never commit `.env` files or expose database credentials and application secrets.

The application also supports a `DATABASE_URL` environment variable for hosted PostgreSQL deployments.

### 5. Create the PostgreSQL database

Create a database named:

```sql
CREATE DATABASE ledgerline_db;
```

Ensure that the database user has the required permissions.

### 6. Start the Flask backend

Run from the `backend/` directory:

```powershell
python run.py
```

Backend URL:

`http://127.0.0.1:5001`

Health check:

`http://127.0.0.1:5001/api/health`

### 7. Start the frontend

Open a separate terminal:

```powershell
cd LedgerLine/frontend
npm install
npm run dev
```

Frontend development URL:

`http://127.0.0.1:5173`

The Vite development server proxies `/api` requests to the Flask backend running on port `5001`.

### 8. Create a production frontend build

```powershell
npm run build
```

The production build is generated in the `frontend/dist/` directory.

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

Financial transaction requests use an idempotency key supplied through the `Idempotency-Key` request header.

Refer to [docs/API.md](docs/API.md) for additional API details.

## Verification and Testing

The project was verified through automated backend tests and manual API, frontend, and database checks.

### Automated Test Results

**Latest previously verified result: 15 tests passed.**

Run the test suite from the `backend/` directory:

```powershell
python -m pytest -v
```

Automated tests cover:

- User registration, login, and profile retrieval.
- Duplicate registration and invalid login rejection.
- Protected endpoint authentication.
- Account ownership restrictions.
- Deposit processing and idempotent retries.
- Reused idempotency keys with different request payloads.
- Invalid transaction amount validation.
- Insufficient balance rejection.
- Transfer ledger debit-credit verification.
- User-specific transaction history.
- Simultaneous withdrawal protection.

### Concurrency Verification

A dedicated concurrency test sends two simultaneous ₹80 withdrawal requests against an account with ₹100.

**Verified expected result:**

- One withdrawal succeeds.
- The other withdrawal is rejected.
- The final account balance remains ₹20.
- The account balance does not become negative.

This verifies the tested concurrent withdrawal scenario; it is not a full-scale load or stress test.

### Manual Verification

Manual checks included:

- Successful deposits, withdrawals, and transfers.
- Exact-request retries.
- Duplicate request protection.
- Rejection of insufficient-balance withdrawals.
- Transaction history access restrictions.
- Account balance reconciliation against ledger entries.
- Double-entry debit-credit verification.

## Deployment Architecture

LedgerLine is deployed using the following services:

| Layer | Platform |
|---|---|
| Frontend | Vercel |
| Backend | Render |
| Database | Neon PostgreSQL |

The frontend communicates with the deployed Flask API over HTTPS. The backend connects to the hosted PostgreSQL database through environment-based configuration.

Production secrets and database credentials are configured through hosting environment variables rather than committed to the repository.

## Current Development Status

### Completed

- Flask backend and PostgreSQL integration.
- JWT authentication and account management.
- Deposits, withdrawals, and transfers.
- Double-entry ledger records for transfers.
- Audit logging.
- Idempotency handling.
- Database transaction and account locking logic.
- Integrated TypeScript frontend.
- Automated backend tests.
- Manual API, frontend, and database verification.
- Concurrent withdrawal scenario testing.
- Production frontend and backend deployment.
- Project documentation and demo video.

### Future Improvements

- Broader automated security and concurrency testing.
- Rate limiting and additional authentication safeguards.
- Database migrations.
- Improved monitoring and operational safeguards.
- Further production security hardening.

## Security Documentation

See [THREATS.md](THREATS.md) for the threat model, identified risks, implemented protections, and known limitations.

## AI Tools Used

ChatGPT (OpenAI) was used as a development assistant for project planning, implementation guidance, debugging, database configuration, API development, testing guidance, documentation, and Git/GitHub workflows.

Generated suggestions and code were reviewed and adapted during development. Testing results are reported only for scenarios that were actually executed.

See [PROMPTS.md](PROMPTS.md) for representative prompts and AI-use disclosure.

## Repository

GitHub: [LedgerLine Repository](https://github.com/Vasanthirangu2006/LedgerLine)

---

**LedgerLine — Every transaction should be accurate, authorized, and traceable.**