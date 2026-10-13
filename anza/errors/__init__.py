"""The single exception type raised by the engine.

Every failure is an :class:`AnzaError` carrying a stable ``code`` (shared with
the Rust and TypeScript engines, see the `Engine Contract
<https://github.com/anzaui/anza/blob/main/docs/engines/contract.md>`_) and a
human-readable ``message``. Messages name a template, never a full filesystem
path, and never contain key material.
"""

from typing import Literal

#: The error codes an :class:`AnzaError` can carry.
ErrorCode = Literal["VALIDATION", "NOT_FOUND", "TEMPLATE", "CRYPTO", "INTERNAL"]


class AnzaError(Exception):
    """An engine error with a stable code.

    ``str(error)`` is ``"[Anza:<code>] <message>"``.

    ============== ==========================================================
    Code           Raised for
    ============== ==========================================================
    ``VALIDATION`` Bad input: an empty route, template or slot, a malformed
                   template name, a template root that does not exist.
    ``NOT_FOUND``  An unknown page route or template, a fragment outside the
                   ``fragments`` allowlist, a template that resolves outside
                   the root or cannot be read.
    ``TEMPLATE``   A template that is not UTF-8, is larger than
                   ``max_template_bytes`` or has an unclosed/empty
                   placeholder.
    ``CRYPTO``     A missing, short or mismatched signing key, and every
                   failed envelope check in :func:`~anza.verify_envelope`.
    ``INTERNAL``   An unexpected engine failure.
    ============== ==========================================================

    Args:
        code: One of the codes above.
        message: What went wrong.

    Attributes:
        code: The error code.
        message: The message, without the ``[Anza:<code>]`` prefix.

    Example:
        >>> from anza import AnzaError
        >>> err = AnzaError.not_found("Page not found")
        >>> err.code, err.message
        ('NOT_FOUND', 'Page not found')
        >>> str(err)
        '[Anza:NOT_FOUND] Page not found'
    """

    def __init__(self, code: ErrorCode, message: str) -> None:
        super().__init__(f"[Anza:{code}] {message}")
        self.code = code
        self.message = message

    @classmethod
    def validation(cls, msg: str) -> "AnzaError":
        """Build a ``VALIDATION`` error."""
        return cls("VALIDATION", msg)

    @classmethod
    def not_found(cls, msg: str) -> "AnzaError":
        """Build a ``NOT_FOUND`` error."""
        return cls("NOT_FOUND", msg)

    @classmethod
    def template(cls, msg: str) -> "AnzaError":
        """Build a ``TEMPLATE`` error."""
        return cls("TEMPLATE", msg)

    @classmethod
    def crypto(cls, msg: str) -> "AnzaError":
        """Build a ``CRYPTO`` error."""
        return cls("CRYPTO", msg)

    @classmethod
    def internal(cls, msg: str) -> "AnzaError":
        """Build an ``INTERNAL`` error."""
        return cls("INTERNAL", msg)
