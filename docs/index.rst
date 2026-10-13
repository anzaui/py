:hide-toc:

.. role:: wavy
.. role:: nudge

.. rst-class:: landing

anza
====

.. rst-class:: hero-badge

|release| · Python engine

.. rst-class:: hero-tagline

Server-templated UI for :wavy:`Python`, :nudge:`signed.`

.. rst-class:: hero-lead

Render full HTML pages and signed JSON fragment envelopes from plain
``.html`` templates. Parsed once at startup, bound with plain Python data,
byte-identical to the Rust and TypeScript engines.

.. code-block:: bash
   :class: hero-code

   # Python 3.10+, installs cryptography>=42
   pip install anza

.. rst-class:: hero-actions

- :doc:`Get started <guide/setup>`
- :doc:`API reference <api/index>`
- `GitHub <https://github.com/anzaui/py>`__
- `PyPI <https://pypi.org/project/anza/>`__

Overview
--------

.. automodule:: anza
   :no-index:

Install
-------

.. code-block:: bash

   pip install anza

``anza`` needs Python 3.10 or newer. Its only dependency is
``cryptography>=42``, which provides Ed25519 and is installed with the
package.

Next steps
----------

- :doc:`guide/setup`: the template root, fragment allowlist, escaping, size
  limit and reloading.
- :doc:`guide/rendering`: pages, fragments, data binding and escaping.
- :doc:`guide/signing`: keys, the v2 signature and :func:`~anza.verify_envelope`.
- :doc:`guide/streaming`: SSE and WebSocket framing.
- :doc:`guide/adapters`: FastAPI, Flask, ASGI and WSGI helpers.
- :doc:`api/index`: every public class and function.
- `Engine Contract <https://github.com/anzaui/anza/blob/main/docs/engines/contract.md>`__:
  the behaviour shared by the Rust, TypeScript and Python engines.
- `Changelog <https://github.com/anzaui/py/blob/main/CHANGELOG.md>`__ and the
  `Anza docs <https://anza.aduki.org/docs>`__.

.. toctree::
   :hidden:

   Introduction <self>

.. toctree::
   :caption: Guide
   :hidden:

   guide/setup
   guide/rendering
   guide/signing
   guide/streaming
   guide/adapters

.. toctree::
   :caption: API reference
   :hidden:

   Overview <api/index>
   api/operations
   api/engine
   api/templates
   api/results
   api/signing
   api/streaming
   api/errors
   api/adapters
