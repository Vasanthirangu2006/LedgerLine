# LedgerLine – AI Prompts and Development Assistance

## 1. Purpose

This document records representative AI assistance used during LedgerLine development. The entries below are paraphrased summaries of development prompts, not verbatim conversation transcripts.

AI was used as a development aid. Suggestions were reviewed, adapted, and tested rather than accepted blindly.

## 2. Dated Prompt Log

### Entry 1 — 2026-11-06: Backend Architecture

**Prompt:** Help structure a Flask backend using SQLAlchemy and PostgreSQL for a digital banking simulation. Include user authentication, accounts, transactions, ledger entries, and audit logs.

**Purpose:** Plan the backend architecture and database models.

### Entry 2 — 2026-11-06: Authentication and Access Control

**Prompt:** Review JWT authentication and protected Flask routes. Check whether users can access only their own accounts and transaction data, and identify missing authorization checks.

**Purpose:** Review authentication and account ownership protection.

### Entry 3 — 2026-11-06: Audit Trail and Transaction Integrity

**Prompt:** Review the transaction and ledger design. Explain how audit logs, debit and credit entries, database transactions, and idempotency keys can help maintain traceability and prevent duplicate operations.

**Purpose:** Examine financial record consistency and auditability.

### Entry 4 — 2026-11-07: Testing and Error Handling

**Prompt:** Suggest test cases for registration, login, account ownership, invalid transaction amounts, insufficient funds, duplicate requests, transfers, and concurrent withdrawals.

**Purpose:** Validate important backend behaviour and identify edge cases.

### Entry 5 — 2026-11-07: Deployment and Integration

**Prompt:** Help deploy a Flask API with Gunicorn and PostgreSQL, configure the production frontend API URL, and troubleshoot cross-origin requests between the Vercel frontend and deployed backend.

**Purpose:** Deploy and verify frontend-backend integration.

## 3. Other Areas of AI Assistance

- SQLAlchemy database models and relationships.
- TypeScript and Vite frontend development.
- Deposit, withdrawal, and transfer implementation.
- Idempotency and error handling.
- PostgreSQL configuration.
- Threat-model and project documentation preparation.

## 4. Human Review and Validation

AI-generated suggestions were treated as guidance, not verified facts.

Validation activities included:

- Reviewing generated code before integration.
- Running backend tests.
- Checking API responses during manual testing.
- Testing authentication and account ownership.
- Verifying transaction balances and ledger entries.
- Building the frontend for production.
- Checking the deployed frontend and backend.

## 5. Responsible AI Use

- No real banking credentials or customer financial records were intentionally provided in prompts.
- Application secrets and database passwords should remain outside source code and AI prompts.
- Generated code was reviewed before integration.
- Final implementation and project decisions remain the developer's responsibility.

## 6. Disclosure

AI assistance supported implementation, debugging, documentation, and testing. It does not replace developer understanding, code review, or independent security validation.