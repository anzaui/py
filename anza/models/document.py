"""The result of a page render."""

from dataclasses import dataclass


@dataclass
class Document:
    """A rendered page, from :class:`~anza.Page`.

    ``str(document)`` is the HTML.

    Example:
        >>> from anza import Page, Setup
        >>> doc = Page("/", {"title": "Hi"}).run(Setup(root="templates").run())
        >>> str(doc) == doc.html
        True
        >>> doc.to_bytes()[:12]
        b'<html><body>'
    """

    #: The full HTML document.
    html: str

    def __str__(self) -> str:
        return self.html

    def to_bytes(self) -> bytes:
        """The HTML encoded as UTF-8, ready for a response body."""
        return self.html.encode("utf-8")
