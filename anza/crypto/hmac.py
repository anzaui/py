"""HMAC-SHA256 signatures in lowercase hex (available as ``anza.hmac``)."""

import hmac
import hashlib
from typing import Union
from .hex import decode_length


def sign(secret: Union[str, bytes], data: Union[str, bytes]) -> str:
    """HMAC-SHA256 of ``data`` under ``secret``, as lowercase hex.

    This low-level helper does not enforce a key length; envelope signing
    (:class:`~anza.SignOptions`) requires a secret of at least 32 bytes.

    Args:
        secret: The key; a ``str`` is encoded as UTF-8.
        data: The message; a ``str`` is encoded as UTF-8.

    Returns:
        str: 64 lowercase hex characters.

    Example:
        >>> from anza import hmac
        >>> sig = hmac.sign("k" * 32, "hi")
        >>> sig
        '1afd7d962ebfcf74a55488bdd29cb42e6da37404b5ed234e30ca6d8831252a84'
        >>> hmac.verify("k" * 32, "hi", sig), hmac.verify("k" * 32, "hi", sig.upper())
        (True, False)
    """
    secret_bytes = secret.encode("utf-8") if isinstance(secret, str) else secret
    data_bytes = data.encode("utf-8") if isinstance(data, str) else data
    return hmac.new(secret_bytes, data_bytes, hashlib.sha256).hexdigest()


def verify(secret: Union[str, bytes], data: Union[str, bytes], signature_hex: str) -> bool:
    """Verify a lowercase-hex HMAC-SHA256 signature in constant time.

    Args:
        secret: The key; a ``str`` is encoded as UTF-8.
        data: The signed message.
        signature_hex: The signature to check.

    Returns:
        bool: ``True`` when it matches. Malformed signatures (wrong length,
        non-hex, uppercase) return ``False`` rather than raising.
    """
    actual = decode_length(signature_hex, 32)
    if actual is None:
        return False
    try:
        secret_bytes = secret.encode("utf-8") if isinstance(secret, str) else secret
        data_bytes = data.encode("utf-8") if isinstance(data, str) else data
        expected = hmac.new(secret_bytes, data_bytes, hashlib.sha256).digest()
        return hmac.compare_digest(expected, actual)
    except Exception:
        return False
