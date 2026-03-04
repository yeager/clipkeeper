"""
ClipKeeper - Secure encrypted storage for clipboard history.

Uses Fernet (AES-128-CBC + HMAC) encryption with a machine-derived key.
Falls back to XOR obfuscation if cryptography package is not available.
"""

import base64
import hashlib
import json
import os
import stat
from pathlib import Path
from typing import Optional

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False


def _get_machine_id() -> str:
    """Get a stable machine identifier for key derivation."""
    # Try /etc/machine-id (systemd)
    for path in ["/etc/machine-id", "/var/lib/dbus/machine-id"]:
        try:
            with open(path) as f:
                return f.read().strip()
        except (FileNotFoundError, PermissionError):
            continue

    # Fallback: hostname + username
    import getpass
    return f"{os.uname().nodename}:{getpass.getuser()}"


def _derive_key(salt: bytes) -> bytes:
    """Derive a Fernet key from machine identity."""
    machine_id = _get_machine_id().encode()

    if HAS_CRYPTO:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100_000,
        )
        return base64.urlsafe_b64encode(kdf.derive(machine_id))
    else:
        # Simple fallback: SHA-256 of machine_id + salt
        return hashlib.sha256(machine_id + salt).digest()


def _xor_bytes(data: bytes, key: bytes) -> bytes:
    """Simple XOR obfuscation fallback."""
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


class SecureStorage:
    """Encrypted file storage for sensitive clipboard data."""

    SALT_SIZE = 16
    MAGIC = b"CKPR"  # ClipKeeper magic bytes

    def __init__(self, path: Path):
        self.path = path

    def save(self, data: dict) -> None:
        """Encrypt and save data to file."""
        plaintext = json.dumps(data).encode("utf-8")
        salt = os.urandom(self.SALT_SIZE)
        key = _derive_key(salt)

        if HAS_CRYPTO:
            fernet = Fernet(key)
            ciphertext = fernet.encrypt(plaintext)
        else:
            ciphertext = _xor_bytes(plaintext, key)

        blob = self.MAGIC + salt + ciphertext

        # Write atomically with restrictive permissions
        tmp_path = self.path.with_suffix(".tmp")
        fd = os.open(str(tmp_path), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        try:
            os.write(fd, blob)
        finally:
            os.close(fd)
        tmp_path.rename(self.path)

        # Ensure file permissions are 600
        os.chmod(str(self.path), stat.S_IRUSR | stat.S_IWUSR)

    def load(self) -> Optional[dict]:
        """Load and decrypt data from file."""
        if not self.path.exists():
            return None

        try:
            blob = self.path.read_bytes()
        except PermissionError:
            return None

        # Check magic
        if not blob.startswith(self.MAGIC):
            # Might be old plaintext JSON — migrate
            return self._migrate_plaintext(blob)

        salt = blob[len(self.MAGIC):len(self.MAGIC) + self.SALT_SIZE]
        ciphertext = blob[len(self.MAGIC) + self.SALT_SIZE:]
        key = _derive_key(salt)

        try:
            if HAS_CRYPTO:
                fernet = Fernet(key)
                plaintext = fernet.decrypt(ciphertext)
            else:
                plaintext = _xor_bytes(ciphertext, key)

            return json.loads(plaintext.decode("utf-8"))
        except Exception:
            return None

    def _migrate_plaintext(self, blob: bytes) -> Optional[dict]:
        """Migrate old plaintext JSON history to encrypted format."""
        try:
            data = json.loads(blob.decode("utf-8"))
            # Re-save encrypted
            self.save(data)
            return data
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None
