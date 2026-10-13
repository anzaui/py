# Signing & Verification

Signed envelopes let a server or edge that relays fragments check that they
came from the origin unchanged. Signing is off by default.

```python
from anza import Setup, SignOptions

Setup(root="./templates", signing=SignOptions(mode="hmac", secret="<at least 32 bytes>"))
Setup(root="./templates", signing=SignOptions(mode="ed25519", private_key="<64 lowercase hex chars>"))
Setup(root="./templates")  # mode="none": no signature
```

`SignOptions(mode, secret, private_key, public_key)` is checked once, in
`Setup.run()`. A bad key raises `AnzaError` with code `CRYPTO`:

- `hmac` needs a `secret` (str or bytes) of at least 32 bytes.
- `ed25519` needs a `private_key` as a 32-byte seed (`bytes`), 64-char
  lowercase hex, or a `cryptography` `Ed25519PrivateKey`. An optional
  `public_key` must match it.

The validated key is `engine.signer`. `repr` of `SignOptions`, `Signer` and
`Engine` never prints key material.

The signature covers the v2 message built by `signature_message(ts, slot,
html, css)` (also `envelope.message()`). Check a received envelope with
`verify_envelope`:

```python
import json
from anza import VerifyKey, verify_envelope

envelope = json.loads(body)
verify_envelope(VerifyKey.hmac(secret), envelope, max_age_secs=60, slot="feed")
verify_envelope(VerifyKey.ed25519(public_key), envelope, max_age_secs=60, slot="feed")
engine.verify_envelope(envelope, max_age_secs=60, slot="feed")  # the engine's own key
```

Each call returns `None` or raises `AnzaError` with code `CRYPTO` (for example
`envelope expired` or `slot mismatch`). See
[Cryptographic Verification](https://anza.aduki.org/docs/engines/crypto) in the anza repo.
