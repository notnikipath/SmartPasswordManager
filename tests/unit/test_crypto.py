from __future__ import annotations

from core.crypto.aes_gcm import AesGcmCipher
from core.crypto.key_derivation import derive_key, generate_salt, hash_master_password, verify_master_password


def test_derive_key_is_deterministic() -> None:
    salt = b"1234567890abcdef"
    first = derive_key("master-pass", salt, iterations=10_000)
    second = derive_key("master-pass", salt, iterations=10_000)
    assert first == second
    assert len(first) == 32


def test_verify_master_password() -> None:
    salt = generate_salt()
    hashed = hash_master_password("my-secret", salt, 50_000)
    assert verify_master_password("my-secret", salt, 50_000, hashed)
    assert not verify_master_password("wrong", salt, 50_000, hashed)


def test_aes_gcm_roundtrip() -> None:
    key = derive_key("encryption", b"abcd1234abcd1234", iterations=20_000)
    cipher = AesGcmCipher(key)
    token = cipher.encrypt_text("super-value", associated_data=b"test")
    plain = cipher.decrypt_text(token, associated_data=b"test")
    assert plain == "super-value"
