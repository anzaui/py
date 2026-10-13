"""The fragment envelope (wire format v2)."""

import json
from dataclasses import dataclass
from typing import Any, Optional

from ..crypto.envelope import ENVELOPE_VERSION, signature_message


@dataclass
class Envelope:
    """A rendered fragment on the wire, envelope format v2.

    Produced by :class:`~anza.Fragment`. The JSON form is
    ``{"v":2,"slot":...,"ts":...,"html":...,"sig":...}`` (``sig`` and ``css``
    only when set), byte-identical to the Rust and TypeScript engines (see
    the `Engine Contract
    <https://github.com/anzaui/anza/blob/main/docs/engines/contract.md>`_).

    Example:
        >>> from anza import Envelope
        >>> env = Envelope(slot="feed", ts=1700000000, html="<p>Hi</p>")
        >>> env.to_json()
        '{"v":2,"slot":"feed","ts":1700000000,"html":"<p>Hi</p>"}'
        >>> env.to_dict()["v"]
        2
    """

    #: The client slot the HTML is for.
    slot: str
    #: Render time, in Unix seconds.
    ts: int
    #: The rendered HTML.
    html: str
    #: Lowercase-hex signature over :meth:`message`, or ``None`` when the
    #: engine does not sign.
    sig: Optional[str] = None
    #: Optional CSS shipped with the HTML; covered by the signature.
    css: Optional[str] = None
    #: Wire-format version, always 2 for envelopes this engine produces.
    v: int = ENVELOPE_VERSION

    def message(self) -> bytes:
        """The exact bytes the signature covers.

        Returns:
            bytes: ``signature_message(ts, slot, html, css)``, see
            :func:`~anza.signature_message`.
        """
        return signature_message(self.ts, self.slot, self.html, self.css)

    def to_dict(self) -> dict[str, Any]:
        """The envelope as a JSON-ready dict.

        Returns:
            dict: ``v``, ``slot``, ``ts`` and ``html``, plus ``sig`` and
            ``css`` when they are set.
        """
        data: dict[str, Any] = {
            "v": self.v,
            "slot": self.slot,
            "ts": self.ts,
            "html": self.html,
        }
        if self.sig is not None:
            data["sig"] = self.sig
        if self.css is not None:
            data["css"] = self.css
        return data

    def to_json(self) -> str:
        """Compact JSON, byte-identical to the Rust and TypeScript engines.

        Returns:
            str: The JSON text, ``v`` first, no whitespace.
        """
        data = self.to_dict()
        # Identical output either way for ASCII text; the ASCII encoder is faster.
        ascii_only = all(v.isascii() for v in data.values() if isinstance(v, str))
        return json.dumps(data, separators=(",", ":"), ensure_ascii=ascii_only)
