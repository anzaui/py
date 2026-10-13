"""Raw WSGI responses for pages and envelopes."""

from typing import Any, Callable
from ..models.document import Document
from ..models.envelope import Envelope


def send_html(start_response: Callable[..., Any], doc: Document, status: str = "200 OK") -> list[bytes]:
    """Start a WSGI HTML response and return its body.

    Args:
        start_response: The WSGI ``start_response`` callable.
        doc: The page from :class:`~anza.Page`.
        status: The WSGI status line.

    Returns:
        list[bytes]: The body iterable to return from the WSGI app.
    """
    body = doc.to_bytes()
    headers = [
        ("Content-Type", "text/html; charset=utf-8"),
        ("Content-Length", str(len(body))),
    ]
    start_response(status, headers)
    return [body]


def send_json(start_response: Callable[..., Any], envelope: Envelope, status: str = "200 OK") -> list[bytes]:
    """Start a WSGI JSON response for an envelope and return its body.

    Args:
        start_response: The WSGI ``start_response`` callable.
        envelope: The envelope from :class:`~anza.Fragment`.
        status: The WSGI status line.

    Returns:
        list[bytes]: The body iterable (:meth:`Envelope.to_json()
        <anza.Envelope.to_json>` as UTF-8).
    """
    body = envelope.to_json().encode("utf-8")
    headers = [
        ("Content-Type", "application/json; charset=utf-8"),
        ("Content-Length", str(len(body))),
    ]
    start_response(status, headers)
    return [body]
