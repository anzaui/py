"""Template digests."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Manifest:
    """Template names mapped to the SHA-256 digest of their source.

    Build one with :meth:`CacheStore.manifest() <anza.CacheStore.manifest>`
    to compare template versions across servers or deployments.

    Example:
        >>> from anza import Manifest
        >>> m = Manifest()
        >>> m.insert("feed/card.html", "ab12")
        >>> m.get("feed/card.html"), m.get("other.html")
        ('ab12', None)
    """

    #: Lowercase-hex SHA-256 digests by template name.
    templates: dict[str, str] = field(default_factory=dict)

    def insert(self, name: str, digest: str) -> None:
        """Record the digest of the template called ``name``."""
        self.templates[name] = digest

    def get(self, name: str) -> Optional[str]:
        """The digest of the template called ``name``, or ``None``."""
        return self.templates.get(name)
