# LedgerLine – Threat Model

## 1. Overview

LedgerLine is a digital banking simulation built with a Flask backend, PostgreSQL database, and TypeScript frontend.

This document identifies potential security threats, their impact, and the protections implemented or recommended.

## 2. Assets to Protect

- User credentials and account information
- Account balances
- Transaction records
- Ledger entries
- Authentication tokens
- Audit logs
- Database credentials and application secrets

## 3. Potential Threats and Mitigations

| Threat | Potential Impact | Mitigation |
|---|---|---|
| Unauthorized access | Attackers access another user's data | JWT-protected endpoints and ownership checks |
| Credential attacks | Unauthorized account access | Password hashing and authentication validation |
| SQL injection | Unauthorized database access or modification | SQLAlchemy ORM and parameterized database operations |
| Invalid transaction amounts | Incorrect balance changes | Server-side amount validation and decimal arithmetic |
| Insufficient funds | Account balance becomes invalid | Balance validation before withdrawal |
| Duplicate requests | A transaction may be processed more than once | Idempotency keys |
| Concurrent withdrawals | Multiple requests may spend the same funds | Database transaction handling and concurrency controls |
| Unauthorized transfers | Money is moved from another user's account | Account ownership validation |
| Data tampering | Transaction records are modified improperly | Ledger entries and audit logging |
| Cross-origin requests | Unauthorized websites attempt API access | Flask-CORS origin restrictions |
| Secret exposure | Attackers obtain database or JWT credentials | Environment variables; secrets must not be committed to Git |

## 4. Existing Security Measures

The application includes:

- JWT-based authentication.
- Password hashing through the backend authentication implementation.
- Authenticated API routes.
- Account ownership validation.
- Server-side transaction validation.
- Decimal-based monetary calculations.
- Idempotency handling for supported transaction requests.
- Database-backed transaction and ledger records.
- Audit logging.
- Restricted CORS configuration for the deployed frontend.

## 5. Known Limitations and Future Improvements

The following areas require further hardening before this prototype could be considered production-ready:

- Add rate limiting to login and registration endpoints.
- Introduce multi-factor authentication.
- Use database migrations instead of relying on automatic table creation.
- Add stronger monitoring and alerting for suspicious activity.
- Review token expiration, revocation, and refresh-token handling.
- Perform independent security testing and penetration testing.
- Review role-based access control and administrative permissions.
- Improve backup, recovery, and disaster-response procedures.
- Use HTTPS for all production communication.
- Review audit-log immutability and retention policies.

## 6. Security Disclaimer

LedgerLine is an educational banking simulation developed as a hiring challenge project. It is not a real banking platform and has not undergone independent security certification or penetration testing.

The controls described here reflect the application's intended implementation and should not be interpreted as a guarantee of complete security.
