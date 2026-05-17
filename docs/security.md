# Security Design

## Cryptography

- Master password is never stored in plaintext.
- Master password hash: PBKDF2-HMAC-SHA256 with random salt and 390000 iterations.
- Encryption of records: AES-256-GCM with unique random nonce per field.
- SQLCipher key is derived from master password via PBKDF2 and applied through `PRAGMA key`.

## Data storage

- Vault database is local only (`vault.db`) and opened with SQLCipher key.
- Metadata file (`vault.meta.json`) stores only salt, hash, and iteration count.
- Sensitive fields (`username`, `password`, `url`, `notes`) are encrypted before writing to DB.
- All DB queries use parameterized statements to protect from SQL injection.
- Local fallback to `sqlite3` is available for development only.
- In Docker, strict mode `SPM_REQUIRE_SQLCIPHER=1` is enabled: startup fails if SQLCipher is unavailable.

## Memory and runtime safety

- Login fields are cleared immediately after successful authentication.
- Master password is used only to derive session keys and not persisted.
- Clipboard manager supports automatic cleanup after configurable timeout.

## Audit and observability

- Security events are written to rotating audit log (`audit.log`):
  - successful/failed login attempts
  - entry creation/update/deletion
  - encrypted export events

## Implemented optional improvements

1. Security audit logs (Group A.2)
2. Clipboard auto-clear (Group A.3)
3. PBKDF2 with salt and iterations (Group A.4)
4. Vulnerability analysis for weak/reused passwords (Group C.1)
