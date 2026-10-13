# Streaming

Envelopes stream over Server-Sent Events or WebSocket with the same JSON as
a fetch response.

## Server-Sent Events

```python
import asyncio
from fastapi.responses import StreamingResponse
from anza import Fragment, format_event

@app.get("/feed/stream")
async def stream_feed():
    async def events():
        while True:
            envelope = Fragment("feed/card.html", "feed", {"title": "Push"}).run(engine)
            yield format_event(envelope)   # 'event: template\ndata: {"v":2,...}\n\n'
            await asyncio.sleep(2)
    return StreamingResponse(events(), media_type="text/event-stream")
```

The JSON is `envelope.to_json()`: compact, UTF-8, `v` first, byte-identical to
the Rust and TypeScript engines. `format_packet(envelope)` returns the same
JSON for WebSocket messages. `Stream(template, slot, params).run(engine)`
returns the SSE text in one call. See [Real-Time Streaming](https://anza.aduki.org/docs/engines/streaming) in the anza repo.
