"""Server-Sent Events framing."""

from ..models.envelope import Envelope


def format_event(envelope: Envelope) -> str:
    """Frame an envelope as one Server-Sent Event.

    Args:
        envelope: The envelope to send.

    Returns:
        str: ``"event: template\\ndata: <envelope JSON>\\n\\n"``. The JSON is
        a single line, so one ``data:`` field is enough.

    Example:
        >>> from anza import Envelope, format_event
        >>> format_event(Envelope(slot="feed", ts=1700000000, html="<p>Hi</p>"))
        'event: template\\ndata: {"v":2,"slot":"feed","ts":1700000000,"html":"<p>Hi</p>"}\\n\\n'
    """
    return f"event: template\ndata: {envelope.to_json()}\n\n"
