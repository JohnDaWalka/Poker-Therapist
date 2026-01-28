"""
PQC-Protected API Client Mixin
==============================
Add post-quantum encryption to any HTTP client.

Usage:
    class MyAPI(PQCApiMixin):
        def __init__(self):
            super().__init__(server_public_key=SERVER_PUB_KEY)
        
        def send_secure(self, data):
            encrypted = self.pqc_encrypt(json.dumps(data).encode())
            return self._post("/api/secure", encrypted)
"""

import base64
import json
from typing import Dict, Any, Optional
from pathlib import Path

try:
    from .pqc import PQCrypto, PQCKeyStore
except ImportError:
    from pqc import PQCrypto, PQCKeyStore


class PQCApiMixin:
    """Mixin to add PQC encryption to API clients."""
    
    def __init__(self, server_public_key: bytes = None, key_name: str = None):
        self._pqc = PQCrypto()
        self._store = PQCKeyStore()
        
        if server_public_key:
            self._server_pub_key = server_public_key
        elif key_name:
            self._server_pub_key = self._store.load_public_key(key_name)
        else:
            self._server_pub_key = None
    
    def pqc_encrypt(self, data: bytes) -> str:
        """Encrypt data and return base64-encoded string."""
        if not self._server_pub_key:
            raise ValueError("No server public key configured")
        encrypted = self._pqc.encrypt(data, self._server_pub_key)
        return base64.b64encode(encrypted).decode()
    
    def pqc_decrypt(self, data: str, private_key: bytes) -> bytes:
        """Decrypt base64-encoded encrypted data."""
        encrypted = base64.b64decode(data)
        return self._pqc.decrypt(encrypted, private_key)
    
    def pqc_sign_request(self, method: str, path: str, body: bytes, private_key: bytes) -> str:
        """Sign an API request."""
        message = f"{method}:{path}:{base64.b64encode(body).decode()}".encode()
        signature = self._pqc.sign(message, private_key)
        return base64.b64encode(signature).decode()


class PQCSecureSession:
    """Secure session with PQC key exchange."""
    
    def __init__(self):
        self._pqc = PQCrypto()
        self._session_key = None
        self._server_pub_key = None
    
    def initiate(self) -> Dict[str, str]:
        """
        Start a secure session. Returns client's ephemeral public key.
        Server should respond with encapsulated shared secret.
        """
        self._ephemeral_key = self._pqc.generate_encryption_keypair()
        return {
            "client_public_key": base64.b64encode(self._ephemeral_key.public_key).decode(),
            "algorithm": self._ephemeral_key.algorithm
        }
    
    def establish(self, server_response: Dict[str, str]) -> bool:
        """
        Complete session establishment with server's encapsulated secret.
        """
        encapsulated = base64.b64decode(server_response["encapsulated_secret"])
        self._session_key = self._pqc._kem.decaps(
            self._ephemeral_key.private_key, 
            encapsulated
        )
        return True
    
    def encrypt_message(self, message: bytes) -> bytes:
        """Encrypt a message using the session key."""
        if not self._session_key:
            raise ValueError("Session not established")
        # Use session key directly with AES
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        import os
        nonce = os.urandom(12)
        aesgcm = AESGCM(self._session_key[:32])
        ciphertext = aesgcm.encrypt(nonce, message, None)
        return nonce + ciphertext
