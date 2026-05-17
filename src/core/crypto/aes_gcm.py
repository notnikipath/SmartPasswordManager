from __future__ import annotations

import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class AesGcmCipher:
    def __init__(self, key: bytes):
        if len(key) != 32:
            raise ValueError("AES-256 key must be 32 bytes long")
        self._aesgcm = AESGCM(key)

    def encrypt_text(self, plaintext: str, associated_data: bytes | None = None) -> str:
        nonce = os.urandom(12)
        encrypted = self._aesgcm.encrypt(nonce, plaintext.encode("utf-8"), associated_data)
        return base64.b64encode(nonce + encrypted).decode("ascii")

    def decrypt_text(self, token: str, associated_data: bytes | None = None) -> str:
        payload = base64.b64decode(token.encode("ascii"))
        nonce = payload[:12]
        ciphertext = payload[12:]
        plain = self._aesgcm.decrypt(nonce, ciphertext, associated_data)
        return plain.decode("utf-8")
