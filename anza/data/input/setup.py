"""Setup: load the templates once and build the :class:`~anza.Engine`.

:class:`~anza.Setup` describes where the templates are and how to render and
sign them. :meth:`Setup.run() <anza.Setup.run>` validates the root and the
signing keys, loads and parses every ``.html`` file under ``root`` and
returns the :class:`~anza.Engine` that :class:`~anza.Page`,
:class:`~anza.Fragment` and :class:`~anza.Stream` render with.

.. code-block:: python

    from anza import Setup, SignOptions

    engine = Setup(
        root="./templates",
        signing=SignOptions(mode="hmac", secret=secret),  # 32+ bytes
        fragments=["feed/", "partials/menu.html"],        # fragment allowlist
        escape=True,                                       # escape {{x}}, keep {{{x}}} raw
        max_template_bytes=512 * 1024,                     # default 1 MiB
        watch=True,                                        # reload on change
    ).run()

    engine.close()  # stops the watcher

.. rubric:: Template layout

Templates are named by their path relative to ``root``, with ``/``
separators: ``pages/home.html``, ``layout/shell.html``, ``feed/card.html``.

- ``pages/`` holds the page templates :class:`~anza.Page` resolves routes to
  (``/`` is ``pages/home.html``, ``pages/index.html`` is the catch-all).
- ``layout/shell.html`` is the optional document every page goes into, as
  ``{{content}}``.
- Any other template can be rendered as a fragment, unless ``fragments``
  limits them.

A template name is a relative path: not empty, no leading ``/``, no ``\\``
or NUL, and no empty, ``.`` or ``..`` segment. A malformed name is a
``VALIDATION`` error. Lookups only use the templates loaded at setup: a
cache miss is ``NOT_FOUND`` and request input never reaches the filesystem.

.. rubric:: Options

- ``fragments`` limits which templates a fragment can render. An entry ending
  in ``/`` allows that prefix, any other entry that exact name. Anything else
  is reported as ``Template '<name>' not found``. Empty (the default) allows
  every template.
- ``escape`` HTML-escapes ``{{slot}}`` values; ``{{{slot}}}`` stays raw.
  **Off by default**: values are inserted as is.
- ``max_template_bytes`` makes a larger file a ``TEMPLATE`` error at load.
- ``watch=True`` starts a polling thread that reloads the templates when
  ``.html`` files are added, changed or removed. Stop it with
  :meth:`Engine.close() <anza.Engine.close>`.
- ``signing`` takes :class:`~anza.SignOptions`; see :doc:`/guide/signing`.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Union
from ...engine.cache.engine import Engine, SignOptions
from ...engine.cache.store import CacheStore
from ...engine.file.load import DEFAULT_MAX_TEMPLATE_BYTES, all as load_all
from ...engine.file.watch import listen
from ...crypto.signer import Signer
from ...errors import AnzaError


@dataclass
class Setup:
    """Where the templates are and how to render and sign them.

    Build one at startup and call :meth:`run` to get the
    :class:`~anza.Engine`.

    Example:
        >>> from anza import Setup, Page
        >>> engine = Setup(root="templates").run()
        >>> Page("/", {"title": "Hello"}).run(engine).html
        '<html><body><h1>Hello</h1></body></html>'

    Warning:
        With the default ``escape=False`` slot values are inserted **without
        HTML escaping**. Turn ``escape`` on, or pass values through
        :func:`~anza.escape_html`, when they can contain user input.
    """

    #: Directory holding the templates (every ``.html`` file under it is
    #: loaded).
    root: Union[str, Path]
    #: How fragments are signed (off by default); keys are validated by
    #: :meth:`run`.
    signing: SignOptions = field(default_factory=SignOptions)
    #: Reload templates when files under ``root`` change (a polling thread;
    #: stop it with :meth:`Engine.close() <anza.Engine.close>`).
    watch: bool = False
    #: Fragment allowlist. Empty (the default) lets fragments use any
    #: template; otherwise an entry ending in ``/`` allows that prefix (e.g.
    #: ``"fragments/"``) and any other entry allows that exact name.
    fragments: list[str] = field(default_factory=list)
    #: HTML-escape ``{{slot}}`` values; ``{{{slot}}}`` stays raw. Off by
    #: default: values are inserted as is.
    escape: bool = False
    #: Refuse template files larger than this (default 1 MiB).
    max_template_bytes: int = DEFAULT_MAX_TEMPLATE_BYTES

    def validate(self) -> None:
        """Check that ``root`` exists and is a directory.

        Raises:
            AnzaError: ``VALIDATION`` when it is missing or not a directory.
        """
        p = Path(self.root)
        if not p.exists():
            raise AnzaError.validation(f"Templates root directory '{self.root}' does not exist")
        if not p.is_dir():
            raise AnzaError.validation(f"Templates root path '{self.root}' is not a directory")

    def run(self) -> Engine:
        """Validate the root and the signing keys, load every template and
        start the watcher when :attr:`watch` is set.

        Returns:
            Engine: The engine to render with. Call
            :meth:`Engine.close() <anza.Engine.close>` to stop the watcher.

        Raises:
            AnzaError: ``VALIDATION`` for a bad root; ``CRYPTO`` for a missing,
                short or mismatched signing key (see :class:`~anza.SignOptions`);
                ``TEMPLATE`` for a template that is not UTF-8, is too large or
                has a malformed placeholder; ``NOT_FOUND`` for a template that
                resolves (through a symlink) outside ``root``.
        """
        self.validate()
        signer = Signer.from_options(self.signing)

        def load() -> dict:
            return load_all(self.root, escape=self.escape, max_bytes=self.max_template_bytes)

        cache = CacheStore(load())
        engine = Engine(self.root, cache, signer, fragments=self.fragments)
        if self.watch:

            def reload() -> None:
                # Swap the whole dict: readers see the old or the new tree.
                cache.templates = load()

            engine.watcher = listen(self.root, reload)
        return engine
