"""The fragment operation: render one template into a JSON envelope."""

from dataclasses import dataclass
from typing import Any, Optional
from ...engine.cache.engine import Engine
from ...errors import AnzaError
from ...models.envelope import Envelope
from ...render.fragment import render_fragment


@dataclass
class Fragment:
    """Render one template into an :class:`~anza.Envelope` for a slot.

    The envelope (wire format v2) carries the slot, a Unix timestamp, the
    rendered HTML and, when the engine signs, a signature over all of them.
    Serialize it with :meth:`Envelope.to_json() <anza.Envelope.to_json>` and
    send it as a fetch response, an SSE event or a WebSocket message.

    Example:
        >>> from anza import Fragment, Setup, SignOptions
        >>> signed = Setup(
        ...     root="templates",
        ...     signing=SignOptions(mode="hmac", secret="a-secret-of-at-least-32-bytes!!!"),
        ... ).run()
        >>> env = Fragment("feed/card.html", "feed", {"title": "New"}).run(signed)
        >>> env.v, env.slot, env.html
        (2, 'feed', '<article>New</article>')
        >>> len(env.sig)  # HMAC-SHA256, lowercase hex
        64

    Warning:
        Values are inserted without HTML escaping unless the engine was set up
        with ``escape=True``.
    """

    #: Template name relative to the root, e.g. ``"feed/card.html"``.
    template: str
    #: The client slot the HTML is for; it is covered by the signature.
    slot: str
    #: The values to bind (see :attr:`Page.params <anza.Page.params>`).
    params: Any = None

    def validate(self) -> None:
        """Check the operation before rendering.

        Raises:
            AnzaError: ``VALIDATION`` when ``template`` or ``slot`` is empty.
        """
        if not self.template:
            raise AnzaError.validation("Template cannot be empty")
        if not self.slot:
            raise AnzaError.validation("Slot cannot be empty")

    def run(self, engine: Engine) -> Envelope:
        """Render the fragment with ``engine``.

        Args:
            engine: The engine from :meth:`Setup.run() <anza.Setup.run>`.

        Returns:
            Envelope: The envelope, signed when the engine has a signing key.

        Raises:
            AnzaError: ``VALIDATION`` for an empty or malformed template name
                or an empty slot; ``NOT_FOUND`` for an unknown template or one
                outside the ``fragments`` allowlist.
        """
        self.validate()
        return render_fragment(engine, self.template, self.slot, self.params)
