"""The engine: loaded templates, the signing key and the render entry points."""

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, Optional, Sequence, Union
from ...crypto.envelope import DEFAULT_SKEW_SECS, _verify_with
from ...crypto.signer import Signer
from ...errors import AnzaError
from ...models.document import Document
from ...models.envelope import Envelope
from ..file.load import Template
from ..name import valid_name
from .store import CacheStore

#: How envelopes are signed: ``"none"`` (no signature), ``"hmac"``
#: (HMAC-SHA256 with a shared secret) or ``"ed25519"`` (Ed25519 with a
#: private key).
SignMode = Literal["none", "hmac", "ed25519"]


@dataclass
class SignOptions:
    """How fragments are signed. Signing is off by default.

    The keys are only checked when :meth:`Setup.run() <anza.Setup.run>`
    builds the :class:`~anza.Signer`; a bad key fails setup, so a running
    engine never signs with a missing, short or mismatched key.

    - ``mode="hmac"`` needs ``secret`` (str or bytes) of **at least 32
      bytes**.
    - ``mode="ed25519"`` needs ``private_key`` as a 32-byte seed
      (``bytes``), 64-char lowercase hex, or a ``cryptography``
      ``Ed25519PrivateKey``. An optional ``public_key`` (same formats, or an
      ``Ed25519PublicKey``) must match it.

    Every signature covers the v2 message from
    :func:`~anza.signature_message`; see :doc:`/guide/signing`.

    Example:
        >>> from anza import SignOptions
        >>> from anza.crypto import ed25519
        >>> seed, public = ed25519.keypair()
        >>> SignOptions(mode="ed25519", private_key=seed.hex())
        SignOptions(mode='ed25519', private_key=<redacted>)
        >>> SignOptions(mode="hmac", secret="a-secret-of-at-least-32-bytes!!!")
        SignOptions(mode='hmac', secret=<redacted>)

    Note:
        ``repr`` never prints key material, so options can be logged.
    """

    #: The signing algorithm.
    mode: SignMode = "none"
    #: The HMAC secret (``mode="hmac"``), at least 32 bytes.
    secret: Optional[Union[str, bytes]] = None
    #: The Ed25519 private key (``mode="ed25519"``).
    private_key: Any = None
    #: Optional Ed25519 public key; setup fails when it does not match
    #: :attr:`private_key`.
    public_key: Any = None

    def __repr__(self) -> str:
        parts = [f"mode={self.mode!r}"]
        if self.secret is not None:
            parts.append("secret=<redacted>")
        if self.private_key is not None:
            parts.append("private_key=<redacted>")
        if self.public_key is not None:
            parts.append("public_key=<set>")
        return f"SignOptions({', '.join(parts)})"


class Engine:
    """Loaded templates plus the validated signing key.

    Build it with :meth:`Setup.run() <anza.Setup.run>` rather than directly.
    An engine is safe to share between threads and requests: renders only
    read the template cache, and a reload (``watch=True``) swaps the whole
    cache at once.

    Args:
        root: The template root directory.
        cache: The loaded templates.
        signing: :class:`~anza.SignOptions` (validated here) or an already
            built :class:`~anza.Signer`; ``None`` disables signing.
        fragments: The fragment allowlist (see :attr:`Setup.fragments
            <anza.Setup.fragments>`).

    Raises:
        AnzaError: ``CRYPTO`` when ``signing`` holds a bad key.

    Example:
        >>> from anza import Setup
        >>> engine = Setup(root="templates").run()
        >>> engine.render_fragment("feed/card.html", "feed", {"title": "Hi"}).html
        '<article>Hi</article>'
        >>> engine.close()
    """

    def __init__(
        self,
        root: Union[str, Path],
        cache: CacheStore,
        signing: Union[SignOptions, Signer, None] = None,
        fragments: Optional[Sequence[str]] = None,
    ) -> None:
        #: The template root directory.
        self.root = Path(root)
        #: The loaded templates, by name.
        self.cache = cache
        #: The validated signing key (``repr`` is redacted).
        self.signer = signing if isinstance(signing, Signer) else Signer.from_options(signing or SignOptions())
        #: Fragment allowlist (see ``Setup.fragments``).
        self.fragments: tuple[str, ...] = tuple(fragments or ())
        #: The template watcher when ``Setup.watch`` is on.
        self.watcher: Any = None

    def close(self) -> None:
        """Stop the template watcher, if any."""
        if self.watcher is not None:
            self.watcher.close()
            self.watcher = None

    def __repr__(self) -> str:
        return f"Engine(root={str(self.root)!r}, templates={len(self.cache.templates)}, signer={self.signer!r})"

    def get_template(self, name: str) -> Template:
        """Look a template up by name.

        Only the templates loaded at setup are searched; the filesystem is
        never touched.

        Args:
            name: Template name relative to the root, e.g. ``"feed/card.html"``.

        Returns:
            Template: The parsed template.

        Raises:
            AnzaError: ``VALIDATION`` for a malformed name (empty, leading
                ``/``, ``\\``, NUL, or an empty, ``.`` or ``..`` segment);
                ``NOT_FOUND`` when no such template was loaded.
        """
        if not valid_name(name):
            raise AnzaError.validation("Invalid template name")
        tpl = self.cache.get(name)
        if tpl is None:
            raise AnzaError.not_found(f"Template '{name}' not found")
        return tpl

    def verify_envelope(
        self,
        envelope: Any,
        *,
        max_age_secs: int,
        slot: str,
        skew_secs: int = DEFAULT_SKEW_SECS,
        now: Optional[int] = None,
    ) -> None:
        """Verify an envelope against this engine's own key.

        Uses the HMAC secret, or the public half of the Ed25519 key, and runs
        the same checks as :func:`~anza.verify_envelope`.

        Args:
            envelope: An :class:`~anza.Envelope` or the parsed JSON ``dict``.
            max_age_secs: Oldest accepted envelope, in seconds.
            slot: The slot the envelope must be for.
            skew_secs: Tolerance for a timestamp ahead of this clock.
            now: The current Unix time (defaults to ``time.time()``).

        Returns:
            None: When the envelope is valid.

        Raises:
            AnzaError: ``CRYPTO`` when signing is off, or when a check fails
                (the message names it, see :func:`~anza.verify_envelope`).

        Example:
            >>> from anza import Fragment, Setup, SignOptions
            >>> signed = Setup(
            ...     root="templates",
            ...     signing=SignOptions(mode="hmac", secret="a-secret-of-at-least-32-bytes!!!"),
            ... ).run()
            >>> env = Fragment("feed/card.html", "feed", {"title": "Hi"}).run(signed)
            >>> signed.verify_envelope(env.to_dict(), max_age_secs=60, slot="feed")
            >>> signed.verify_envelope(env.to_dict(), max_age_secs=60, slot="menu")
            Traceback (most recent call last):
                ...
            anza.errors.AnzaError: [Anza:CRYPTO] slot mismatch
        """
        if self.signer.mode == "none":
            raise AnzaError.crypto("signing is off")
        _verify_with(envelope, self.signer.verify, max_age_secs, slot, skew_secs, now)

    def render_page(self, route: str, params: Any = None) -> Document:
        """Render the page for ``route``; same as ``Page(route, params).run(self)``.

        See :class:`~anza.Page` for the route rules.

        Args:
            route: The request path, e.g. ``"/"``.
            params: The values to bind.

        Returns:
            Document: The rendered HTML document.

        Raises:
            AnzaError: ``NOT_FOUND`` for an unknown or malformed route.
        """
        from ...render.page import render_page
        return render_page(self, route, params)

    def render_fragment(
        self,
        template_name: str,
        slot: str,
        params: Any = None,
    ) -> Envelope:
        """Render a fragment; same as ``Fragment(template_name, slot, params).run(self)``.

        Args:
            template_name: Template name relative to the root.
            slot: The client slot the HTML is for.
            params: The values to bind.

        Returns:
            Envelope: The envelope, signed when the engine has a key.

        Raises:
            AnzaError: ``VALIDATION`` for a malformed name; ``NOT_FOUND`` for an
                unknown template or one outside the ``fragments`` allowlist.
        """
        from ...render.fragment import render_fragment
        return render_fragment(self, template_name, slot, params)
