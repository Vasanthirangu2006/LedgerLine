# LedgerLine – AI Prompts and Development Assistance

## 1. Purpose

This document records representative AI prompts and the areas where AI assistance was used during the development of LedgerLine.

AI was used as a development aid. Generated suggestions were reviewed, adapted, and tested rather than accepted blindly.

## 2. Areas Where AI Assistance Was Used

- Backend architecture and Flask route development.
- SQLAlchemy database models and relationships.
- JWT authentication and authorization.
- Transaction validation and error handling.
- Ledger-entry consistency and idempotency.
- Frontend TypeScript implementation.
- PostgreSQL and deployment configuration.
- Documentation and threat-model preparation.
- Debugging and test-case design.

## 3. Representative Prompts

### Backend Development

"Help design a Flask backend using SQLAlchemy and PostgreSQL for a digital banking simulation. Include users, accounts, transactions, ledger entries, and audit logs."

### Authentication

"Review a Flask JWT authentication implementation. Identify missing authentication checks, account ownership checks, and possible security issues."

### Transaction Processing

"Help implement deposit, withdrawal, and account-to-account transfer operations. Validate amounts, prevent insufficient-funds withdrawals, and use database transactions."

### Idempotency

"Explain how idempotency keys can prevent duplicate financial transaction requests. Suggest an implementation and relevant test cases."

### Database Design

"Review the relationships between users, bank accounts, transactions, ledger entries, and audit logs. Identify possible integrity issues."

### Frontend Development

"Help build a TypeScript and Vite banking dashboard with account information, transaction history, deposit, withdrawal, and transfer interfaces."

### Testing

"Suggest test cases for registration, login, account ownership, invalid amounts, insufficient funds, duplicate requests, transfers, and concurrent withdrawals."

### Deployment

"Help configure a Flask application with Gunicorn and PostgreSQL for deployment, and connect a Vite frontend to the deployed API."

### Security Review

"Create a threat model for an educational digital banking application. Identify assets, attack scenarios, mitigations, and remaining limitations."

## 4. Human Review and Validation

AI-generated suggestions were treated as guidance, not verified facts.

Development validation included:

- Reviewing generated code before integration.
- Running the backend test suite.
- Checking API responses during manual testing.
- Testing authentication and account ownership.
- Verifying transaction balances and ledger entries.
- Building the frontend for production.
- Testing the deployed frontend and backend.

## 5. Responsible AI Use

- No real banking credentials or customer financial records were intentionally provided in prompts.
- Application secrets and database passwords should remain outside source code and AI prompts.
- Generated code must be reviewed for correctness and security.
- Final implementation and project decisions remain the developer's responsibility.

## 6. Disclosure

AI assistance supported implementation, debugging, documentation, and testing activities. It does not replace developer understanding, code review, or independent security validation.
