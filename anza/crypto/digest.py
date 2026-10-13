"""SHA-256 digests (available as ``anza.digest``)."""

import hashlib
from typing import Union


def hash(data: Union[str, bytes]) -> bytes:
    """SHA-256 of ``data`` (a ``str`` is encoded as UTF-8).

    Example:
        >>> from anza import digest
        >>> digest.hash("hi")[:4]
        b'\\x8fCCF'
    """
    buf = data.encode("utf-8") if isinstance(data, str) else data
    return hashlib.sha256(buf).digest()


def hex(data: Union[str, bytes]) -> str:
    """Lowercase-hex SHA-256 of ``data`` (a ``str`` is encoded as UTF-8).

    This is the digest of :attr:`Template.digest <anza.Template.digest>`.

    Example:
        >>> from anza import digest
        >>> digest.hex("hi")
        '8f434346648f6b96df89dda901c5176b10a6d83961dd3c1ac88b59b2dc327aa4'
    """
    buf = data.encode("utf-8") if isinstance(data, str) else data
    return hashlib.sha256(buf).hexdigest()
