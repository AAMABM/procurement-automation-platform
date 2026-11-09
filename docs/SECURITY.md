# Security Model

## Authentication
- Argon2id (OWASP-recommended parameters).
- Access JWT: 15 min, `HS256` (RS256 in a multi-service deployment).
- Refresh JWT: 7 days, rotation in Phase 2.
- Constant-time login failure to prevent user enumeration.

## Authorization (RBAC)
- Enforced by `require_permissions(...)` dependency at route boundary.
- Permission codes are catalogued in `app/core/permissions.py`.
- `is_superuser` grants wildcard (`*`) — audited via logs.

## Auditing
- Every request tagged with `X-Request-ID`.
- Structured JSON logs ready for SIEM ingestion.
- `created_at`, `updated_at`, `last_login_at`, `deleted_at` on identity tables.

## Hardening checklist (Phase 1)
- [x] No secrets in git
- [x] Non-root Docker user
- [x] CORS restricted to configured origins
- [x] Docs disabled in `production`
- [x] Centralized exception handling — no leakage
- [x] Fail-fast on placeholder secret in production
- [ ] Phase 2: refresh-token rotation + revocation list
- [ ] Phase 2: rate limiting on `/auth/login`
- [ ] Phase 3: MFA / WebAuthn
- [ ] Phase 4: Attribute-Based Access Control for approvals