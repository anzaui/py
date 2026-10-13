"""FastAPI / Starlette responses for pages and envelopes."""

from typing import Any
from ..models.document import Document
from ..models.envelope import Envelope


def html_response(doc: Document, status_code: int = 200) -> Any:
    """Wrap a rendered page in an HTML response.

    Args:
        doc: The page from :class:`~anza.Page`.
        status_code: The HTTP status.

    Returns:
        A ``fastapi.responses.HTMLResponse`` (or Starlette's); the bare HTML
        string when neither FastAPI nor Starlette is installed.
    """
    try:
        from fastapi.responses import HTMLResponse
        return HTMLResponse(content=doc.html, status_code=status_code)
    except ImportError:
        try:
            from starlette.responses import HTMLResponse
            return HTMLResponse(content=doc.html, status_code=status_code)
        except ImportError:
            return doc.html


def json_response(envelope: Envelope, status_code: int = 200) -> Any:
    """Wrap a fragment envelope in a JSON response.

    Args:
        envelope: The envelope from :class:`~anza.Fragment`.
        status_code: The HTTP status.

    Returns:
        A ``fastapi.responses.JSONResponse`` (or Starlette's) of
        :meth:`Envelope.to_dict() <anza.Envelope.to_dict>`; the bare dict when
        neither FastAPI nor Starlette is installed.
    """
    try:
        from fastapi.responses import JSONResponse
        return JSONResponse(content=envelope.to_dict(), status_code=status_code)
    except ImportError:
        try:
            from starlette.responses import JSONResponse
            return JSONResponse(content=envelope.to_dict(), status_code=status_code)
        except ImportError:
            return envelope.to_dict()
