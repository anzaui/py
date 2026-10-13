"""Envelope signatures, wire format v2 (see the `Engine Contract
<https://github.com/anzaui/anza/blob/main/docs/engines/contract.md>`_).

::

    message  = "anza-sig-v2\\n" field(ts) field(slot) field(html) field(css)
    field(x) = <decimal UTF-8 byte length of x> ":" x "\\n"

``ts`` is written in decimal; an absent ``css`` is the empty string.
"""

import time
from dataclasses import dataclass
from typing import Any, Callable, Mapping, Optional, Union

from ..errors import AnzaError
from . import ed25519 as _ed25519
from . import hmac as _hmac
from .hex import decode
from .signer import HMAC_MIN_SECRET, public_key as _public_key

#: Envelope wire-format version produced and accepted by this engine.
ENVELOPE_VERSION = 2

#: Domain-separation prefix of every v2 signature message.
SIGNATURE_DOMAIN = b"anza-sig-v2\n"

#: Default tolerance for a timestamp ahead of the verifier's clock.
DEFAULT_SKEW_SECS = 5


def _field(value: str) -> bytes:
    raw = value.encode("utf-8")
    return b"%d:%s\n" % (len(raw), raw)


def signature_message(ts: int, slot: str, html: str, css: Optional[str] = None) -> bytes:
    """The exact bytes a v2 envelope signature covers.

    Every field is length-prefixed, so no two different envelopes produce
    the same message.

    Args:
        ts: The envelope timestamp, in Unix seconds.
        slot: The envelope slot.
        html: The envelope HTML.
        css: The envelope CSS; ``None`` signs as the empty string.

    Returns:
        bytes: ``anza-sig-v2\\n`` followed by ``<len>:<value>\\n`` for ``ts``,
        ``slot``, ``html`` and ``css``.

    Example:
        >>> from anza import signature_message
        >>> signature_message(1700000000, "feed", "<p>Hi</p>")
        b'anza-sig-v2\\n10:1700000000\\n4:feed\\n9:<p>Hi</p>\\n0:\\n'
    """
    return SIGNATURE_DOMAIN + _field(str(ts)) + _field(slot) + _field(html) + _field(css or "")


@dataclass(frozen=True)
class VerifyKey:
    """The key :func:`verify_envelope` checks a signature with.

    Build it with :meth:`hmac` or :meth:`ed25519`. The key is validated when
    it is used: a short HMAC secret or a malformed public key fails the
    verification with ``CRYPTO`` ``invalid verification key``. ``repr`` never
    prints the key.

    Example:
        >>> from anza import VerifyKey
        >>> VerifyKey.hmac("a-secret-of-at-least-32-bytes!!!")
        VerifyKey(mode='hmac', key=<redacted>)
    """

    #: ``"hmac"`` or ``"ed25519"``.
    mode: str
    #: The shared HMAC secret.
    secret: Union[str, bytes, None] = None
    #: The Ed25519 public key.
    public_key: Any = None

    @classmethod
    def hmac(cls, secret: Union[str, bytes]) -> "VerifyKey":
        """A key for HMAC-SHA256 envelopes.

        Args:
            secret: The shared secret, at least 32 bytes.
        """
        return cls(mode="hmac", secret=secret)

    @classmethod
    def ed25519(cls, public_key: Any) -> "VerifyKey":
        """A key for Ed25519 envelopes.

        Args:
            public_key: 32 bytes, 64-char lowercase hex, or an
                ``Ed25519PublicKey``.
        """
        return cls(mode="ed25519", public_key=public_key)

    def __repr__(self) -> str:
        return f"VerifyKey(mode={self.mode!r}, key=<redacted>)"


def _get(envelope: Any, name: str) -> Any:
    if isinstance(envelope, Mapping):
        return envelope.get(name)
    return getattr(envelope, name, None)


def _verify_with(
    envelope: Any,
    check_sig: Callable[[bytes, str], bool],
    max_age_secs: int,
    slot: str,
    skew_secs: int,
    now: Optional[int],
) -> None:
    v = _get(envelope, "v")
    if isinstance(v, bool) or v != ENVELOPE_VERSION:
        raise AnzaError.crypto("unsupported envelope version")
    ts, env_slot, html, css, sig = (_get(envelope, k) for k in ("ts", "slot", "html", "css", "sig"))
    if (
        not isinstance(ts, int)
        or isinstance(ts, bool)
        or ts < 0
        or not isinstance(env_slot, str)
        or not isinstance(html, str)
        or (css is not None and not isinstance(css, str))
    ):
        raise AnzaError.crypto("malformed envelope")
    if sig is None:
        raise AnzaError.crypto("envelope is not signed")
    if not isinstance(sig, str) or decode(sig) is None:
        raise AnzaError.crypto("malformed signature")
    current = int(time.time()) if now is None else now
    if ts > current + skew_secs:
        raise AnzaError.crypto("envelope timestamp is in the future")
    if current - ts > max_age_secs:
        raise AnzaError.crypto("envelope expired")
    if env_slot != slot:
        raise AnzaError.crypto("slot mismatch")
    if not check_sig(signature_message(ts, env_slot, html, css), sig):
        raise AnzaError.crypto("bad signature")


def verify_envelope(
    key: VerifyKey,
    envelope: Any,
    *,
    max_age_secs: int,
    slot: str,
    skew_secs: int = DEFAULT_SKEW_SECS,
    now: Optional[int] = None,
) -> None:
    """Verify a received envelope.

    The checks run in order, and the first failure raises:

    1. the key is usable (``invalid verification key``);
    2. ``v`` is 2 (``unsupported envelope version``);
    3. ``ts`` is a non-negative integer, ``slot`` and ``html`` are strings,
       ``css`` is absent or a string (``malformed envelope``);
    4. ``sig`` is present (``envelope is not signed``) and lowercase hex
       (``malformed signature``);
    5. ``ts`` is at most ``skew_secs`` ahead of ``now`` (``envelope timestamp
       is in the future``) and at most ``max_age_secs`` old (``envelope
       expired``);
    6. the envelope is for ``slot`` (``slot mismatch``);
    7. the signature over :func:`signature_message` matches, compared in
       constant time (``bad signature``).

    Args:
        key: The verification key, see :class:`VerifyKey`.
        envelope: An :class:`~anza.Envelope` or the parsed JSON ``dict``.
        max_age_secs: Oldest accepted envelope, in seconds.
        slot: The slot the envelope must be for.
        skew_secs: Tolerance for a timestamp ahead of the verifier's clock.
        now: The current Unix time (defaults to ``time.time()``).

    Returns:
        None: When the envelope is valid.

    Raises:
        AnzaError: ``CRYPTO``, with the failed check as the message.

    Example:
        >>> from anza import Envelope, VerifyKey, hmac, verify_envelope
        >>> secret = "a-secret-of-at-least-32-bytes!!!"
        >>> env = Envelope(slot="feed", ts=1700000000, html="<p>Hi</p>")
        >>> env.sig = hmac.sign(secret, env.message())
        >>> key = VerifyKey.hmac(secret)
        >>> verify_envelope(key, env.to_dict(), max_age_secs=60, slot="feed", now=1700000010)
        >>> verify_envelope(key, env.to_dict(), max_age_secs=60, slot="feed", now=1700000100)
        Traceback (most recent call last):
            ...
        anza.errors.AnzaError: [Anza:CRYPTO] envelope expired

    Warning:
        A valid signature alone does not stop replays: always pass the slot
        you expect and a ``max_age_secs`` that fits the use.
    """
    if key.mode == "hmac":
        secret = key.secret.encode("utf-8") if isinstance(key.secret, str) else key.secret
        if not isinstance(secret, (bytes, bytearray)) or len(secret) < HMAC_MIN_SECRET:
            raise AnzaError.crypto("invalid verification key")
        check = lambda msg, sig: _hmac.verify(bytes(secret), msg, sig)  # noqa: E731
    elif key.mode == "ed25519":
        try:
            pub = _public_key(key.public_key)
        except AnzaError:
            raise AnzaError.crypto("invalid verification key") from None
        check = lambda msg, sig: _ed25519.verify(pub, msg, sig)  # noqa: E731
    else:
        raise AnzaError.crypto("invalid verification key")
    _verify_with(envelope, check, max_age_secs, slot, skew_secs, now)
