"""WebSocket message framing."""

from ..models.envelope import Envelope


def format_packet(envelope: Envelope) -> str:
    """The WebSocket text message for an envelope: its compact JSON.

    Args:
        envelope: The envelope to send.

    Returns:
        str: :meth:`Envelope.to_json() <anza.Envelope.to_json>`.

    Example:
        >>> from anza import Envelope, format_packet
        >>> format_packet(Envelope(slot="feed", ts=1700000000, html="<p>Hi</p>"))
        '{"v":2,"slot":"feed","ts":1700000000,"html":"<p>Hi</p>"}'
    """
    return envelope.to_json()
