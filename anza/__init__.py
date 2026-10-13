"""Anza server-templated UI (STUI) engine for Python.

``anza`` renders full HTML pages and signed JSON fragment envelopes from
plain ``.html`` templates with ``{{slot}}`` placeholders. Templates are
loaded and parsed once, at startup; a render is a dictionary lookup per slot
and one string format. It needs Python 3.10+ and ``cryptography>=42`` (for
Ed25519, installed with the package); everything else is the standard
library.

The engine follows the shared `Engine Contract
<https://github.com/anzaui/anza/blob/main/docs/engines/contract.md>`_, so it
renders the same bytes, envelopes and signatures as the Rust and TypeScript
engines.

The public API is re-exported here:

- Operations: :class:`Setup` (load templates, build an :class:`Engine`),
  :class:`Page`, :class:`Fragment` and :class:`Stream`.
- Results: :class:`Document` (a page), :class:`Envelope` (a fragment, wire
  format v2) and :class:`Manifest`.
- Signing: :class:`SignOptions`, :class:`Signer`, :class:`VerifyKey`,
  :func:`verify_envelope`, :func:`signature_message` and the
  :mod:`~anza.crypto.hmac`, :mod:`~anza.crypto.ed25519`,
  :mod:`~anza.crypto.hkdf` and :mod:`~anza.crypto.digest` modules.
- Templates: :class:`Template`, :class:`Chunk`, :func:`extract`,
  :func:`string` and :func:`escape_html`.
- Streaming: :func:`format_event` (SSE) and :func:`format_packet` (WebSocket).
- Errors: :class:`AnzaError`.

Framework helpers live in :mod:`anza.adapters`.

Example:
    Load the templates once, then render a page and a signed fragment::

        from anza import Fragment, Page, Setup, SignOptions

        engine = Setup(
            root="./templates",
            signing=SignOptions(mode="hmac", secret="a-secret-of-at-least-32-bytes!!!"),
        ).run()

        doc = Page("/", {"title": "Home"}).run(engine)          # pages/home.html
        env = Fragment("feed/card.html", "feed", {"title": "New"}).run(engine)
        body = env.to_json()  # {"v":2,"slot":"feed","ts":...,"html":...,"sig":...}

Warning:
    Values are inserted **without HTML escaping** unless the engine is set up
    with ``escape=True`` (see :class:`Setup`). Escape untrusted input with
    :func:`escape_html` or turn the option on.
"""

from .data.input import Setup, Page, Fragment, Stream
from .engine import Engine, CacheStore, SignOptions, SignMode, Template, Chunk, extract, string, escape_html
from .models import Document, Envelope, Manifest
from .errors import AnzaError
from .stream import format_event, format_packet
from .crypto import digest, hmac, ed25519, hkdf
from .crypto.envelope import ENVELOPE_VERSION, VerifyKey, signature_message, verify_envelope
from .crypto.signer import Signer

__all__ = [
    "Setup",
    "Page",
    "Fragment",
    "Stream",
    "Engine",
    "CacheStore",
    "SignOptions",
    "SignMode",
    "Template",
    "Chunk",
    "extract",
    "string",
    "escape_html",
    "Document",
    "Envelope",
    "Manifest",
    "AnzaError",
    "format_event",
    "format_packet",
    "digest",
    "hmac",
    "ed25519",
    "hkdf",
    "ENVELOPE_VERSION",
    "VerifyKey",
    "signature_message",
    "verify_envelope",
    "Signer",
]
