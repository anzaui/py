"""Raw ASGI responses for pages and envelopes."""

from typing import Any, Callable, Awaitable
from ..models.document import Document
from ..models.envelope import Envelope


async def send_html(send: Callable[[dict[str, Any]], Awaitable[None]], doc: Document, status: int = 200) -> None:
    """Send a page as a complete ASGI HTTP response.

    Sends ``http.response.start`` (``content-type: text/html;
    charset=utf-8`` and ``content-length``) and one ``http.response.body``.

    Args:
        send: The ASGI ``send`` callable.
        doc: The page from :class:`~anza.Page`.
        status: The HTTP status.
    """
    body = doc.to_bytes()
    await send(
        {
            "type": "http.response.start",
            "status": status,
            "headers": [
                (b"content-type", b"text/html; charset=utf-8"),
                (b"content-length", str(len(body)).encode("ascii")),
            ],
        }
    )
    await send(
        {
            "type": "http.response.body",
            "body": body,
            "more_body": False,
        }
    )


async def send_json(send: Callable[[dict[str, Any]], Awaitable[None]], envelope: Envelope, status: int = 200) -> None:
    """Send an envelope as a complete ASGI HTTP JSON response.

    The body is :meth:`Envelope.to_json() <anza.Envelope.to_json>`
    (``content-type: application/json; charset=utf-8``).

    Args:
        send: The ASGI ``send`` callable.
        envelope: The envelope from :class:`~anza.Fragment`.
        status: The HTTP status.
    """
    body = envelope.to_json().encode("utf-8")
    await send(
        {
            "type": "http.response.start",
            "status": status,
            "headers": [
                (b"content-type", b"application/json; charset=utf-8"),
                (b"content-length", str(len(body)).encode("ascii")),
            ],
        }
    )
    await send(
        {
            "type": "http.response.body",
            "body": body,
            "more_body": False,
        }
    )
