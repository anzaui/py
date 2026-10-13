"""Ed25519 signing and verification (available as ``anza.ed25519``).

Backed by the ``cryptography`` package (constant-time, RFC 8032). Keys are
exactly 32 bytes, 64-char lowercase hex, or ``cryptography`` key objects;
anything else is rejected. Signatures are 128 lowercase hex characters.
"""

from typing import Any, Tuple, Union

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat

from ..errors import AnzaError
from .hex import decode_length
from .signer import private_key, public_key, raw_public_key


def keypair() -> Tuple[bytes, bytes]:
    """Generate a new Ed25519 key pair.

    Returns:
        tuple[bytes, bytes]: ``(private_seed, public_key)``, 32 bytes each.
        Keep the seed secret; give verifiers the public key.

    Example:
        >>> from anza import ed25519
        >>> seed, public = ed25519.keypair()
        >>> len(seed), len(public)
        (32, 32)
    """
    key = Ed25519PrivateKey.generate()
    seed = key.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())
    return seed, raw_public_key(key)


def sign(key: Any, data: Union[str, bytes]) -> str:
    """Sign ``data`` with an Ed25519 private key.

    Args:
        key: A 32-byte seed, 64-char lowercase hex, or an
            ``Ed25519PrivateKey``.
        data: The message; a ``str`` is encoded as UTF-8.

    Returns:
        str: The signature, 128 lowercase hex characters.

    Raises:
        AnzaError: ``CRYPTO`` for a malformed key.

    Example:
        >>> from anza import ed25519
        >>> seed, public = ed25519.keypair()
        >>> sig = ed25519.sign(seed, "hi")
        >>> len(sig), ed25519.verify(public, "hi", sig), ed25519.verify(public, "ho", sig)
        (128, True, False)
    """
    data_bytes = data.encode("utf-8") if isinstance(data, str) else bytes(data)
    try:
        return private_key(key).sign(data_bytes).hex()
    except AnzaError:
        raise
    except Exception as e:  # pragma: no cover - defensive
        raise AnzaError.crypto(f"Ed25519 signing failed: {type(e).__name__}") from None


def verify(key: Any, data: Union[str, bytes], signature_hex: str) -> bool:
    """Verify a lowercase-hex Ed25519 signature.

    Args:
        key: The public key: 32 bytes, 64-char lowercase hex, or an
            ``Ed25519PublicKey``.
        data: The signed message.
        signature_hex: The signature to check.

    Returns:
        bool: ``True`` when it is valid. Malformed keys or signatures (wrong
        length, non-hex, uppercase) return ``False`` rather than raising.
    """
    sig = decode_length(signature_hex, 64)
    if sig is None:
        return False
    try:
        pub = public_key(key)
    except AnzaError:
        return False
    data_bytes = data.encode("utf-8") if isinstance(data, str) else bytes(data)
    try:
        pub.verify(sig, data_bytes)
        return True
    except InvalidSignature:
        return False
