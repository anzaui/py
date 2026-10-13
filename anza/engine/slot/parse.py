"""Template parsing: ``{{slot}}`` and ``{{{raw}}}`` placeholders."""

from dataclasses import dataclass
from typing import Literal
from ...errors import AnzaError


@dataclass(frozen=True)
class Chunk:
    """One piece of a parsed template.

    ``static`` text, a ``slot`` (``{{name}}``, escaped when the engine runs
    with ``escape=True``) or a ``raw`` slot (``{{{name}}}``, never escaped).

    Example:
        >>> from anza import Chunk
        >>> Chunk(kind="slot", value="title")
        Chunk(kind='slot', value='title')
    """

    #: ``"static"``, ``"slot"`` or ``"raw"``.
    kind: Literal["static", "slot", "raw"]
    #: The static text, or the slot name (whitespace stripped).
    value: str


def extract(template: str) -> list[Chunk]:
    """Split a template into static text and ``{{slot}}`` / ``{{{raw}}}`` chunks.

    Whitespace around a slot name is ignored (``{{ title }}`` is ``title``).

    Args:
        template: The template source.

    Returns:
        list[Chunk]: The chunks in order.

    Raises:
        AnzaError: ``TEMPLATE`` for an unclosed ``{{`` or ``{{{``, or an empty
            placeholder.

    Example:
        >>> from anza import extract
        >>> extract("<p>{{ name }} {{{html}}}</p>")  # doctest: +NORMALIZE_WHITESPACE
        [Chunk(kind='static', value='<p>'), Chunk(kind='slot', value='name'),
         Chunk(kind='static', value=' '), Chunk(kind='raw', value='html'),
         Chunk(kind='static', value='</p>')]
        >>> extract("<p>{{name</p>")
        Traceback (most recent call last):
            ...
        anza.errors.AnzaError: [Anza:TEMPLATE] Unclosed slot placeholder '{{' in template
    """
    chunks: list[Chunk] = []
    cursor = 0
    length = len(template)

    while cursor < length:
        open_idx = template.find("{{", cursor)
        if open_idx == -1:
            chunks.append(Chunk(kind="static", value=template[cursor:]))
            break

        if open_idx > cursor:
            chunks.append(Chunk(kind="static", value=template[cursor:open_idx]))

        raw = template.startswith("{", open_idx + 2)
        start = open_idx + (3 if raw else 2)
        close = "}}}" if raw else "}}"
        close_idx = template.find(close, start)
        if close_idx == -1:
            if raw:
                raise AnzaError.template("Unclosed raw slot placeholder '{{{' in template")
            raise AnzaError.template("Unclosed slot placeholder '{{' in template")

        slot_name = template[start:close_idx].strip()
        if not slot_name:
            raise AnzaError.template("Empty slot placeholder {{}} in template")

        chunks.append(Chunk(kind="raw" if raw else "slot", value=slot_name))
        cursor = close_idx + len(close)

    return chunks
