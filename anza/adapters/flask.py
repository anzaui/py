"""Flask responses for pages and envelopes."""

from typing import Any
from ..models.document import Document
from ..models.envelope import Envelope


def html_response(doc: Document, status_code: int = 200) -> Any:
    """Wrap a rendered page in an HTML response.

    Args:
        doc: The page from :class:`~anza.Page`.
        status_code: The HTTP status.

    Returns:
        A ``flask.Response`` with ``text/html``; the bare HTML string when
        Flask is not installed.
    """
    try:
        from flask import Response
        return Response(doc.html, status=status_code, mimetype="text/html")
    except ImportError:
        return doc.html


def json_response(envelope: Envelope, status_code: int = 200) -> Any:
    """Wrap a fragment envelope in a JSON response.

    Args:
        envelope: The envelope from :class:`~anza.Fragment`.
        status_code: The HTTP status.

    Returns:
        A ``flask.jsonify`` response of :meth:`Envelope.to_dict()
        <anza.Envelope.to_dict>`; the bare dict when Flask is not installed.
    """
    try:
        from flask import jsonify
        resp = jsonify(envelope.to_dict())
        resp.status_code = status_code
        return resp
    except ImportError:
        return envelope.to_dict()
