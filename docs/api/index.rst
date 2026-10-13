API reference
=============

Everything below is importable from the top-level ``anza`` package
(``from anza import Setup``), except the framework helpers in
:mod:`anza.adapters`. Every page is generated from the docstrings in the
source.

.. currentmodule:: anza

Operations
----------

.. autosummary::

   Setup
   Page
   Fragment
   Stream

Engine and templates
--------------------

.. autosummary::

   Engine
   SignOptions
   SignMode
   CacheStore
   Template
   Chunk
   extract
   string
   escape_html

Results
-------

.. autosummary::

   Document
   Envelope
   Manifest

Signing and verification
------------------------

.. autosummary::

   Signer
   VerifyKey
   verify_envelope
   signature_message
   ENVELOPE_VERSION
   crypto.hmac
   crypto.ed25519
   crypto.hkdf
   crypto.digest

Streaming
---------

.. autosummary::

   format_event
   format_packet

Errors
------

.. autosummary::

   AnzaError

Adapters
--------

.. autosummary::

   adapters.fastapi
   adapters.flask
   adapters.asgi
   adapters.wsgi
