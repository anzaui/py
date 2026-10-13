"""Streaming envelopes over Server-Sent Events and WebSocket.

Envelopes stream with the same JSON as a fetch response:
:meth:`Envelope.to_json() <anza.Envelope.to_json>`, compact UTF-8 with ``v``
first, byte-identical to the Rust and TypeScript engines.

- :func:`~anza.format_event` frames an envelope as one SSE event
  (``event: template``).
- :func:`~anza.format_packet` returns the JSON for one WebSocket text
  message.
- :class:`Stream(template, slot, params).run(engine) <anza.Stream>` renders
  and frames an SSE event in one call.

.. rubric:: Server-Sent Events (FastAPI)

.. code-block:: python

    import asyncio
    from fastapi.responses import StreamingResponse
    from anza import Fragment, format_event

    @app.get("/feed/stream")
    async def stream_feed():
        async def events():
            while True:
                envelope = Fragment("feed/card.html", "feed", {"title": "Push"}).run(engine)
                yield format_event(envelope)   # 'event: template\\ndata: {"v":2,...}\\n\\n'
                await asyncio.sleep(2)
        return StreamingResponse(events(), media_type="text/event-stream")

.. rubric:: WebSocket (Starlette / FastAPI)

.. code-block:: python

    from anza import Fragment, format_packet

    @app.websocket("/feed/ws")
    async def feed_ws(ws):
        await ws.accept()
        envelope = Fragment("feed/card.html", "feed", {"title": "Push"}).run(engine)
        await ws.send_text(format_packet(envelope))

Receivers verify streamed envelopes like any other, with
:func:`~anza.verify_envelope`.
"""

from .sse import format_event
from .ws import format_packet

__all__ = ["format_event", "format_packet"]
