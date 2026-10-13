"""HTML escaping, identical in all three engines: ``&`` ``<`` ``>`` ``"`` ``'``
become ``&amp;`` ``&lt;`` ``&gt;`` ``&quot;`` ``&#39;``. Safe for element
content and quoted attribute values. (``html.escape`` writes ``&#x27;``.)"""

_TABLE = str.maketrans({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"})


def escape_html(text: str) -> str:
    """HTML-escape ``text`` for element content or a quoted attribute value.

    ``&`` ``<`` ``>`` ``"`` ``'`` become ``&amp;`` ``&lt;`` ``&gt;``
    ``&quot;`` ``&#39;``, byte for byte like the Rust and TypeScript engines
    (``html.escape`` writes ``&#x27;`` instead).

    Args:
        text: The text to escape.

    Returns:
        str: The escaped text.

    Example:
        >>> from anza import escape_html
        >>> escape_html('''<a href="x">Tom & Jerry's</a>''')
        '&lt;a href=&quot;x&quot;&gt;Tom &amp; Jerry&#39;s&lt;/a&gt;'
    """
    return text.translate(_TABLE)
