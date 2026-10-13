"""The stream operation: render one template as a Server-Sent Event."""

from dataclasses import dataclass
from typing import Any, Optional
from ...engine.cache.engine import Engine
from ...errors import AnzaError
from ...render.fragment import render_fragment
from ...stream.sse import format_event


@dataclass
class Stream:
    """Render one template as a Server-Sent Event in one call.

    Equivalent to ``format_event(Fragment(template, slot, params).run(engine))``,
    see :func:`~anza.format_event` and :doc:`/guide/streaming`.

    Example:
        >>> from anza import Setup, Stream
        >>> engine = Setup(root="templates").run()
        >>> text = Stream("feed/card.html", "feed", {"title": "Push"}).run(engine)
        >>> text.startswith('event: template\\ndata: {"v":2,"slot":"feed",')
        True
        >>> text.endswith('\\n\\n')
        True
    """

    #: Template name relative to the root, e.g. ``"feed/card.html"``.
    template: str
    #: The client slot the HTML is for.
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

    def run(self, engine: Engine) -> str:
        """Render the fragment and frame it as an SSE event.

        Args:
            engine: The engine from :meth:`Setup.run() <anza.Setup.run>`.

        Returns:
            str: ``"event: template\\ndata: <envelope JSON>\\n\\n"``.

        Raises:
            AnzaError: The same errors as :meth:`Fragment.run() <anza.Fragment.run>`.
        """
        self.validate()
        env = render_fragment(engine, self.template, self.slot, self.params)
        return format_event(env)
