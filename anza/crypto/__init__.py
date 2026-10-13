"""Signing and verification of fragment envelopes.

Signed envelopes let a server, edge or client that relays fragments check
that they came from the origin unchanged, for the slot they claim, and
recently. Signing is **off by default**; turn it on with
:class:`~anza.SignOptions`:

.. code-block:: python

    from anza import Setup, SignOptions

    Setup(root="./templates", signing=SignOptions(mode="hmac", secret=secret))
    Setup(root="./templates", signing=SignOptions(mode="ed25519", private_key=seed_hex))
    Setup(root="./templates")  # mode="none": envelopes carry no signature

.. rubric:: Keys

Keys are checked once, in :meth:`Setup.run() <anza.Setup.run>`, which builds
a :class:`~anza.Signer` (``engine.signer``). A bad key raises
:class:`~anza.AnzaError` with code ``CRYPTO``, so a running engine never
signs with a missing, short or mismatched key.

- ``hmac`` needs a ``secret`` (str or bytes) of at least 32 bytes. Both sides
  share it; derive per-purpose keys from one master secret with
  :func:`anza.hkdf.derive_key() <anza.crypto.hkdf.derive_key>`.
- ``ed25519`` needs a ``private_key`` as a 32-byte seed, 64-char lowercase
  hex, or a ``cryptography`` ``Ed25519PrivateKey``; an optional
  ``public_key`` must match it. Verifiers only need the public key
  (``engine.signer.public_key``). Generate a pair with
  :func:`anza.ed25519.keypair() <anza.crypto.ed25519.keypair>`.

``repr`` of :class:`~anza.SignOptions`, :class:`~anza.Signer`,
:class:`~anza.VerifyKey` and :class:`~anza.Engine` never prints key material.
Ed25519 and constant-time comparisons come from the ``cryptography`` package
(``cryptography>=42``, a dependency of ``anza``).

.. rubric:: Signature v2

The signature covers the bytes from :func:`~anza.signature_message` (also
:meth:`Envelope.message() <anza.Envelope.message>`)::

    message  = "anza-sig-v2\\n" field(ts) field(slot) field(html) field(css)
    field(x) = <decimal UTF-8 byte length of x> ":" x "\\n"

Signatures are lowercase hex: 64 characters for HMAC-SHA256, 128 for
Ed25519. Uppercase, odd-length or otherwise malformed hex is rejected, so
a signature has exactly one accepted spelling.

.. rubric:: Verification

Check a received envelope with :func:`~anza.verify_envelope` (or
:meth:`Engine.verify_envelope() <anza.Engine.verify_envelope>` with the
engine's own key):

.. code-block:: python

    import json
    from anza import VerifyKey, verify_envelope

    envelope = json.loads(body)
    verify_envelope(VerifyKey.hmac(secret), envelope, max_age_secs=60, slot="feed")
    verify_envelope(VerifyKey.ed25519(public_key), envelope, max_age_secs=60, slot="feed")
    engine.verify_envelope(envelope, max_age_secs=60, slot="feed")

Each call returns ``None`` or raises :class:`~anza.AnzaError` with code
``CRYPTO`` whose message names the failed check: ``unsupported envelope
version``, ``malformed envelope``, ``envelope is not signed``, ``malformed
signature``, ``envelope timestamp is in the future``, ``envelope expired``,
``slot mismatch`` or ``bad signature``. Always pass the ``slot`` you expect
and a ``max_age_secs`` that fits your use: a valid signature alone does not
stop a replay of an old envelope or one meant for another slot.

The wire format and the checks are specified in the `Engine Contract
<https://github.com/anzaui/anza/blob/main/docs/engines/contract.md>`_.
"""

from . import digest
from . import hex
from . import hmac
from . import ed25519
from . import hkdf
from . import envelope

__all__ = ["digest", "hex", "hmac", "ed25519", "hkdf", "envelope"]
