# Anza Engine: Python Reference

The Anza Python Engine (`anza` on PyPI) renders full HTML pages and signed JSON
fragment envelopes from `.html` templates. It needs Python 3.10+ and
`cryptography>=42`, which `pip install anza` installs. The rest is the
standard library. It follows the shared [Engine Contract](https://anza.aduki.org/docs/engines/contract).

## What You Get

- **Parse once** — `Setup(...).run()` loads every template under the root and splits it into static chunks and `{{slot}}` placeholders
- **Plain Python data** — bind dicts, dataclasses, Pydantic models or any object with attributes
- **Signing** — HMAC-SHA256 or Ed25519 signatures (signature v2), with keys validated at setup
- **Verification** — `verify_envelope` checks version, age, slot and signature
- **Streaming** — `format_event` (SSE) and `format_packet` (WebSocket) encoders, and a `Stream` operation
- **Adapters** — small response helpers for FastAPI/Starlette, Flask, raw ASGI and WSGI

## Installation

```bash
pip install anza
```

## Quickstart (FastAPI)

```python
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from anza import Setup, SignOptions, Page, Fragment

# 1. Load and parse every template once at startup (the secret needs 32+ bytes)
engine = Setup(
    root="./templates",
    signing=SignOptions(mode="hmac", secret="super-secret-key-32-bytes-long!!"),
).run()

app = FastAPI()

# Full page: templates/pages/home.html inside templates/layout/shell.html
# (or inside the default document when there is no shell)
@app.get("/", response_class=HTMLResponse)
async def home():
    doc = Page("/", {"title": "Anza Python"}).run(engine)
    return doc.html

# Fragment: templates/feed/card.html as a signed JSON envelope
@app.get("/card")
async def card():
    envelope = Fragment("feed/card.html", "feed", {"title": "Live Python Card"}).run(engine)
    return JSONResponse(envelope.to_dict())
```

## Flask Integration (WSGI)

```python
from flask import Flask, Response, jsonify
from anza import Setup, Page, Fragment

engine = Setup(root="./templates").run()
app = Flask(__name__)

@app.route("/")
def home():
    doc = Page("/", {"title": "Flask"}).run(engine)
    return Response(doc.html, mimetype="text/html")

@app.route("/card")
def card():
    envelope = Fragment("feed/card.html", "feed", {"title": "Item"}).run(engine)
    return jsonify(envelope.to_dict())
```

`anza.adapters.fastapi`, `anza.adapters.flask`, `anza.adapters.asgi` and
`anza.adapters.wsgi` provide the same responses as helpers (`html_response` /
`json_response`, or `send_html` / `send_json`).

## Guide

- [Setup Options](guide/setup.md): the template root, fragment allowlist, escaping, size limit and reloading.
- [Rendering](guide/rendering.md): pages, data binding and escaping.
- [Signing & Verification](guide/signing.md): keys, the v2 signature and `verify_envelope`.
- [Streaming](guide/streaming.md): SSE and WebSocket framing.

## Package Layout

| Package | Contents |
|---------|----------|
| `anza.data.input` | `Setup`, `Page`, `Fragment`, `Stream` |
| `anza.engine.slot` | `{{slot}}` parser (`extract`), binder (`string`), `escape_html` |
| `anza.engine.file` | Template loading, reading and watching |
| `anza.engine.cache` | `Engine`, `SignOptions`, the template store |
| `anza.render` | `render_page`, `render_fragment` |
| `anza.crypto` | `hmac`, `ed25519`, `hkdf`, `digest` (SHA-256), `hex`, `signer` (`Signer`), `envelope` (`verify_envelope`, `VerifyKey`, `signature_message`) |
| `anza.stream` | `format_event` (SSE), `format_packet` (WebSocket) |
| `anza.adapters` | FastAPI, Flask, ASGI, WSGI helpers |
| `anza.models` | `Document`, `Envelope`, `Manifest` |
