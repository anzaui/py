"""The template store behind :attr:`Engine.cache <anza.Engine.cache>`."""

from typing import Optional
from ..file.load import Template
from ...models.manifest import Manifest


class CacheStore:
    """The loaded templates, by name.

    Lookups are exact: names are never rewritten, so aliases of one file
    (``a/./b.html``, ``\\a\\b.html``) cannot grow the cache. The engine's
    store is :attr:`Engine.cache <anza.Engine.cache>`.

    Args:
        templates: Initial templates by name (empty when omitted).

    Example:
        >>> from anza import Setup
        >>> store = Setup(root="templates").run().cache
        >>> sorted(store.keys())
        ['feed/card.html', 'layout/shell.html', 'pages/home.html']
        >>> store.has("pages/home.html"), store.get("pages/nope.html")
        (True, None)
    """

    def __init__(self, templates: Optional[dict[str, Template]] = None) -> None:
        #: Templates by name. A reload replaces the whole dict.
        self.templates: dict[str, Template] = templates or {}

    def get(self, name: str) -> Optional[Template]:
        """The template called ``name``, or ``None``."""
        return self.templates.get(name)

    def insert(self, name: str, template: Template) -> None:
        """Add or replace the template called ``name``."""
        self.templates[name] = template

    def remove(self, name: str) -> None:
        """Drop the template called ``name``, if present."""
        self.templates.pop(name, None)

    def has(self, name: str) -> bool:
        """Whether a template called ``name`` is loaded."""
        return name in self.templates

    def keys(self) -> list[str]:
        """The names of every loaded template."""
        return list(self.templates.keys())

    def manifest(self) -> Manifest:
        """A :class:`~anza.Manifest` of every template's SHA-256 digest.

        Example:
            >>> from anza import Setup
            >>> m = Setup(root="templates").run().cache.manifest()
            >>> m.get("pages/home.html")
            '4e1df12fd5e679b7bdaafe259f349f94175b4154900ded81942a83707d2a3405'
        """
        m = Manifest()
        for name, tpl in self.templates.items():
            m.insert(name, tpl.digest)
        return m
