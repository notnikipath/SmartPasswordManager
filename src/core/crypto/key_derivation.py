from __future__ import annotations

import base64
import hashlib
import hmac
import os


def generate_salt(length: int = 16) -> bytes:
    return os.urandom(length)


def derive_key(password: str, salt: bytes, iterations: int, length: int = 32) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations, dklen=length)


def hash_master_password(password: str, salt: bytes, iterations: int) -> str:
    key = derive_key(password, salt, iterations)
    return base64.b64encode(key).decode("ascii")


def verify_master_password(password: str, salt: bytes, iterations: int, expected_b64_hash: str) -> bool:
    candidate = hash_master_password(password, salt, iterations)
    return hmac.compare_digest(candidate, expected_b64_hash)
