"""Signing keys, validated and decoded once at setup."""

import hashlib
import hmac as _hmac
from typing import Any, Optional, Union

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from ..errors import AnzaError
from .hex import decode_length

#: Minimum HMAC-SHA256 secret length, in bytes.
HMAC_MIN_SECRET = 32

KeyInput = Union[str, bytes, bytearray, memoryview]


def _raw32(value: Any) -> Optional[bytes]:
    """32 raw bytes, or 64 lowercase hex characters."""
    if isinstance(value, str):
        return decode_length(value, 32)
    if isinstance(value, (bytes, bytearray, memoryview)):
        data = bytes(value)
        return data if len(data) == 32 else None
    return None


def private_key(value: Any) -> Ed25519PrivateKey:
    """Parse an Ed25519 private key (32-byte seed, 64-char hex seed, or an
    ``Ed25519PrivateKey``). Raises ``CRYPTO`` for anything else."""
    if isinstance(value, Ed25519PrivateKey):
        return value
    seed = _raw32(value)
    if seed is None:
        raise AnzaError.crypto("Ed25519 private key must be a 32-byte seed or 64-char hex")
    return Ed25519PrivateKey.from_private_bytes(seed)


def public_key(value: Any) -> Ed25519PublicKey:
    """Parse an Ed25519 public key (32 bytes, 64-char hex, or an
    ``Ed25519PublicKey``). Raises ``CRYPTO`` for anything else."""
    if isinstance(value, Ed25519PublicKey):
        return value
    raw = _raw32(value)
    if raw is None:
        raise AnzaError.crypto("Ed25519 public key must be 32 bytes or 64-char hex")
    try:
        return Ed25519PublicKey.from_public_bytes(raw)
    except ValueError:
        raise AnzaError.crypto("Ed25519 public key is not a valid point") from None


def raw_public_key(key: Union[Ed25519PrivateKey, Ed25519PublicKey]) -> bytes:
    pub = key.public_key() if isinstance(key, Ed25519PrivateKey) else key
    return pub.public_bytes(Encoding.Raw, PublicFormat.Raw)


def _secret_bytes(secret: Any) -> bytes:
    if secret is None:
        return b""
    if isinstance(secret, str):
        return secret.encode("utf-8")
    if isinstance(secret, (bytes, bytearray, memoryview)):
        return bytes(secret)
    raise AnzaError.crypto("HMAC secret must be str or bytes")


class Signer:
    """A validated signing key, built once at setup.

    :meth:`Setup.run() <anza.Setup.run>` builds it from
    :class:`~anza.SignOptions` with :meth:`from_options` and stores it as
    :attr:`Engine.signer <anza.Engine.signer>`. A running engine never signs
    with a missing, short or mismatched key, and ``repr`` never prints key
    material.

    Attributes:
        mode: ``"none"``, ``"hmac"`` or ``"ed25519"``.

    Example:
        >>> from anza import Signer, SignOptions
        >>> signer = Signer.from_options(SignOptions(mode="hmac", secret="k" * 32))
        >>> signer
        Signer(mode='hmac', key=<redacted>)
        >>> sig = signer.sign(b"message")
        >>> signer.verify(b"message", sig), signer.verify(b"other", sig)
        (True, False)
        >>> Signer.from_options(SignOptions(mode="hmac", secret="short"))
        Traceback (most recent call last):
            ...
        anza.errors.AnzaError: [Anza:CRYPTO] HMAC secret must be at least 32 bytes
    """

    __slots__ = ("mode", "_hmac", "_ed25519", "_public")

    def __init__(self) -> None:
        self.mode = "none"
        self._hmac: Any = None
        self._ed25519: Optional[Ed25519PrivateKey] = None
        self._public: Optional[bytes] = None

    @classmethod
    def from_options(cls, options: Any) -> "Signer":
        """Validate ``options`` and decode its keys.

        Args:
            options: A :class:`~anza.SignOptions`; ``None`` disables signing.

        Returns:
            Signer: The validated signer.

        Raises:
            AnzaError: ``CRYPTO`` for an HMAC secret shorter than 32 bytes or
                not str/bytes, a missing or malformed Ed25519 private key, a
                public key that does not match it, or an unknown mode.
        """
        signer = cls()
        mode = getattr(options, "mode", "none") if options is not None else "none"
        signer.mode = mode
        if mode == "none":
            return signer
        if mode == "hmac":
            secret = _secret_bytes(options.secret)
            if len(secret) < HMAC_MIN_SECRET:
                raise AnzaError.crypto(f"HMAC secret must be at least {HMAC_MIN_SECRET} bytes")
            signer._hmac = _hmac.new(secret, digestmod=hashlib.sha256)
            return signer
        if mode == "ed25519":
            if options.private_key is None:
                raise AnzaError.crypto("Ed25519 signing needs a private key")
            key = private_key(options.private_key)
            pub = raw_public_key(key)
            if options.public_key is not None:
                if not _hmac.compare_digest(raw_public_key(public_key(options.public_key)), pub):
                    raise AnzaError.crypto("Ed25519 public key does not match the private key")
            signer._ed25519 = key
            signer._public = pub
            return signer
        raise AnzaError.crypto(f"Unknown signing mode {mode!r}")

    def sign(self, message: bytes) -> Optional[str]:
        """Sign ``message``.

        Args:
            message: The bytes to sign, normally
                :meth:`Envelope.message() <anza.Envelope.message>`.

        Returns:
            str | None: The lowercase-hex signature, or ``None`` when signing
            is off.
        """
        if self._hmac is not None:
            mac = self._hmac.copy()
            mac.update(message)
            return mac.hexdigest()
        if self._ed25519 is not None:
            return self._ed25519.sign(message).hex()
        return None

    def verify(self, message: bytes, signature_hex: str) -> bool:
        """Check a lowercase-hex signature made by this signer, in constant time.

        Args:
            message: The signed bytes.
            signature_hex: The signature to check.

        Returns:
            bool: ``True`` when it matches; always ``False`` when signing is
            off or the signature is malformed.
        """
        if self._hmac is not None:
            actual = decode_length(signature_hex, 32)
            if actual is None:
                return False
            mac = self._hmac.copy()
            mac.update(message)
            return _hmac.compare_digest(mac.digest(), actual)
        if self._ed25519 is not None:
            actual = decode_length(signature_hex, 64)
            if actual is None:
                return False
            try:
                self._ed25519.public_key().verify(actual, message)
                return True
            except InvalidSignature:
                return False
        return False

    @property
    def public_key(self) -> Optional[bytes]:
        """The raw 32-byte Ed25519 public key that verifies this signer's signatures."""
        return self._public

    def __repr__(self) -> str:
        if self.mode == "none":
            return "Signer(mode='none')"
        return f"Signer(mode={self.mode!r}, key=<redacted>)"
