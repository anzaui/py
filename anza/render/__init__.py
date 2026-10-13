"""Rendering pages and fragments.

:class:`~anza.Page` renders a full HTML document and :class:`~anza.Fragment`
renders one template into a JSON :class:`~anza.Envelope` for a client slot.
Both take a dict, ``(key, value)`` pairs, or any object as their params.

.. rubric:: Pages

``Page(route, params)`` maps the route to a template under ``pages/``:

- ``/`` is ``pages/home.html``; ``/about`` and ``/about/`` are
  ``pages/about.html``; ``/docs/intro`` is ``pages/docs/intro.html``.
- When that page does not exist, ``pages/index.html`` is the catch-all.
- Otherwise, or for a malformed route (``..``, ``\\``, NUL),
  :meth:`Page.run() <anza.Page.run>` raises :class:`~anza.AnzaError` with
  code ``NOT_FOUND`` and the message ``Page not found``.

The page markup is inserted as is (no wrapper element) into
``layout/shell.html`` as ``{{content}}``; the shell is bound with ``params``
plus ``content``. Without a shell the page goes into a minimal default
document with a ``<dock-main>`` open shadow root (Declarative Shadow DOM).

.. rubric:: Fragments

``Fragment(template, slot, params)`` renders any loaded template (limited by
the ``fragments`` allowlist of :class:`~anza.Setup`) and returns an
:class:`~anza.Envelope` with the slot, a Unix timestamp, the HTML and, when
the engine signs, a signature (see :doc:`/guide/signing`). Send
:meth:`Envelope.to_json() <anza.Envelope.to_json>` as the response body.

.. rubric:: Data binding

.. code-block:: python

    from dataclasses import dataclass
    from anza import Page

    @dataclass
    class UserProfile:
        user_id: str
        user_name: str
        role: str

    profile = UserProfile(user_id="usr_102", user_name="Alice", role="Admin")
    doc = Page("/profile", profile).run(engine)

``{{user_name}}`` reads ``profile.user_name``. Only public, non-callable
attributes are read: names starting with ``_`` and methods render as empty.
Missing values and ``None`` render as empty, booleans as ``true`` /
``false``, integral floats without ``.0``, and dicts, lists and tuples as
compact JSON (``{"a":1}``). See :func:`~anza.string` for the exact rules.

.. rubric:: Escaping

By default values are inserted **as is, without HTML escaping**. Escape user
input with :func:`~anza.escape_html` before passing it in, or turn on the
``escape`` option:

.. code-block:: python

    from anza import Setup, escape_html

    escape_html('<a href="x">Tom & Jerry\'s</a>')
    # '&lt;a href=&quot;x&quot;&gt;Tom &amp; Jerry&#39;s&lt;/a&gt;'

    engine = Setup(root="./templates", escape=True).run()

With ``escape=True``, ``{{name}}`` is HTML-escaped and ``{{{name}}}`` stays
raw. Use ``{{{content}}}`` in ``layout/shell.html`` so the rendered page is
not escaped twice.
"""

from .page import render_page
from .fragment import render_fragment

__all__ = ["render_page", "render_fragment"]
