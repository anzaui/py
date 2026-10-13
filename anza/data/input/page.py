"""The page operation: render a route into a full HTML document."""

from dataclasses import dataclass
from typing import Any, Optional
from ...engine.cache.engine import Engine
from ...errors import AnzaError
from ...models.document import Document
from ...render.page import render_page


@dataclass
class Page:
    """Render the page for a request route into a full HTML document.

    ``/`` renders ``pages/home.html`` and ``/a/b`` (or ``/a/b/``) renders
    ``pages/a/b.html``. An unknown route falls back to ``pages/index.html``
    when it exists. The page goes into ``layout/shell.html`` as
    ``{{content}}`` (the shell is bound with ``params`` plus ``content``), or
    into a minimal default document with a ``<dock-main>`` open shadow root
    when there is no shell. See :doc:`/guide/rendering`.

    Example:
        >>> from anza import Page, Setup
        >>> engine = Setup(root="templates").run()
        >>> doc = Page("/", {"title": "Home"}).run(engine)
        >>> doc.html
        '<html><body><h1>Home</h1></body></html>'
        >>> Page("/missing/../route").run(engine)
        Traceback (most recent call last):
            ...
        anza.errors.AnzaError: [Anza:NOT_FOUND] Page not found
    """

    #: The request path, e.g. ``"/"`` or ``"/docs/intro"``.
    route: str
    #: Values to bind (a dict, ``(key, value)`` pairs, or any object
    #: whose public attributes are read, such as a dataclass or Pydantic model).
    params: Any = None

    def validate(self) -> None:
        """Check the operation before rendering.

        Raises:
            AnzaError: ``VALIDATION`` when ``route`` is empty.
        """
        if not self.route:
            raise AnzaError.validation("Route cannot be empty")

    def run(self, engine: Engine) -> Document:
        """Render the page with ``engine``.

        Args:
            engine: The engine from :meth:`Setup.run() <anza.Setup.run>`.

        Returns:
            Document: The rendered HTML document.

        Raises:
            AnzaError: ``VALIDATION`` for an empty route; ``NOT_FOUND`` (message
                ``Page not found``) for an unknown or malformed route
                (``..``, ``\\``, NUL) when there is no ``pages/index.html``.
        """
        self.validate()
        return render_page(engine, self.route, self.params)
