# Changelog: anza (Python Engine)

All notable changes to the Python template and STUI streaming engine are documented here.

## [0.7.0](https://github.com/anzaui/py/compare/v0.6.0...v0.7.0) (2026-10-13)


### ⚠ BREAKING CHANGES

* 0.6.0 hardened engine (signature v2, contract, escaping)

### Features

* 0.6.0 hardened engine (signature v2, contract, escaping) ([1fdc17d](https://github.com/anzaui/py/commit/1fdc17db68da8aaa7b7aa3ca384001c87cbce153))
* initial commit of anza python stui engine ([07d49e2](https://github.com/anzaui/py/commit/07d49e21d6039b99fe7a5b0d13665f4ae39851ef))


### Bug Fixes

* **crypto:** implement rfc8032 ed25519 and add readme/license ([086ad30](https://github.com/anzaui/py/commit/086ad30ddf961d86620b71cd988dfc44d7272440))


### Documentation

* add an anza docs site deployed to GitHub Pages ([369413a](https://github.com/anzaui/py/commit/369413a2c750e1330141451d772082c100910946))
* build with plain anza docs (site.base support), logo favicon ([37f3c83](https://github.com/anzaui/py/commit/37f3c83700e503e6ad957ac0b4f9b1425a8eb4d9))
* streamline readme and set copyright to aduki, Labs ([ae19fee](https://github.com/anzaui/py/commit/ae19fee46c4d99231e1e850b13fdcabd877b9574))

## [0.6.0] — 2026-10-13

The hardening release. This repository now versions the engine on its own (from 0.6.0); earlier 0.5.x versions followed the Anza release.

### Added
- `verify_envelope(key, envelope, max_age_secs=..., slot=...)` with `VerifyKey.hmac(...)` / `VerifyKey.ed25519(...)`, and `Engine.verify_envelope`: version, freshness (max age, 5 s future skew), expected slot, then the signature (constant-time). Failures raise `AnzaError` `CRYPTO` with a fixed message per check.
- `escape_html`, the `escape` setup option (`{{x}}` HTML-escaped, `{{{x}}}` raw; default off), `fragments` (fragment allowlist), `max_template_bytes` (default 1 MiB), and a working `watch=True` (polling thread; stop it with `Engine.close()`).
- `anza.crypto.hex` (strict lowercase hex), `Signer`, `signature_message`, `Envelope.to_json()`.
- Golden test fixtures in `tests/fixtures/`: vendored copies of the fixtures shared by the Rust, TypeScript and Python engines (kept in the anza repo under `engines/fixtures/`), checked by the contract tests. The behaviour they pin down is the [Engine Contract](https://anza.aduki.org/docs/engines/contract).

### Changed
- **Breaking: `cryptography>=42` is required.** The `crypto` extra is gone.
- **Breaking: signature v2.** The message is `anza-sig-v2\n` + length-prefixed `ts`, `slot`, `html`, `css` (was `ts:slot:html`); envelopes gain `v` (always 2, first JSON key) and `Envelope.message()` returns bytes.
- **Breaking:** keys are validated in `Setup.run()` (was at render time): a missing or short (< 32 bytes) HMAC secret, an Ed25519 key that is not a 32-byte seed or 64-char lowercase hex, or a mismatched `public_key` raises `CRYPTO`. `engine.signing` is replaced by `engine.signer`.
- **Breaking: pages.** `/a/b` renders `pages/a/b.html` (routes are no longer lowercased), then `pages/index.html`, else raises `NOT_FOUND` ("Page not found"). Pages are no longer wrapped in `<page-*>`, the shell is optional, and it gets `{{content}}` only (no `main`, `body`, `route`).
- **Breaking: values.** Booleans render `true`/`false` (were `True`/`False`), integral floats drop `.0`, dicts and lists render as compact JSON.
- SSE/WS/ASGI/WSGI JSON is compact UTF-8, byte-identical to the other engines. Validation messages match them.
- Faster rendering: templates compile once to a `%`-pattern, keys are decoded once, unsigned renders skip the signature message (100-slot fragment, unsigned: 11.4 → 8.2 µs; Ed25519: 95 → 52 µs).
- Documentation is built with `anza docs` and published at https://anzaui.github.io/py/.

### Removed
- The pure-Python Ed25519 fallback, and loading templates from disk on a cache miss.
- **Breaking:** `mode="session"` in `SignOptions`. They never signed anything.

### Security
- Ed25519 went through a pure-Python fallback that was not constant-time and signed with keys of any length.
- `../` in a route could read `.html` files outside the template root, request input could grow the cache through path aliases, NUL gave a 500, and errors leaked absolute paths. Lookups are now cache-only, names are validated, and errors name the template only.
- Hex is strict lowercase; `repr` of `SignOptions`, `Setup`, `Engine` and `Signer` redacts keys; `{{__class__}}`-style names and methods are never read; symlinks that resolve outside the root are not loaded.

## [0.5.1] — 2026-10-12

### Changed
- Version sync with the Anza 0.5.1 release. No engine changes.

## [0.5.0] — 2026-08-27

### Added
- **0 External Runtime Dependencies**: 100% standard library implementation with zero mandatory pip dependencies.
- **Fast Slot Interpolation**: Pre-parsed chunk arrays with optimized list concatenation resolving parameters from dicts, dataclasses, and custom objects.
- **Dual-Mode Rendering**: Mode A full-page Open Declarative Shadow DOM shells (`<page-*><template shadowrootmode="open">...`) and Mode B signed JSON envelopes.
- **Cryptographic Security**: HMAC-SHA256 with constant-time `hmac.compare_digest`, Ed25519 asymmetric origin signing, and HKDF-SHA256 stream keys.
- **Framework Adapters**: Raw ASGI, raw WSGI, FastAPI, and Flask response helpers.
- **Streaming Protocols**: Server-Sent Events (SSE) and WebSocket frame generators.
