"""Sphinx configuration for the anza Python engine docs.

The pages are generated from the docstrings in ``anza/`` (autodoc +
napoleon); the theme is Furo, restyled with the Anza web palette and fonts
(``_static/anza.css``). Build with::

    pip install -e .[docs]
    sphinx-build -W --keep-going -n -b html -d _build/doctrees docs _site
"""

import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import anza  # noqa: E402

release = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["version"]
version = release

project = "anza"
author = "aduki, Labs"
copyright = "2026 aduki, Labs"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
root_doc = "index"
nitpicky = True

# -- autodoc / napoleon ------------------------------------------------------

autodoc_member_order = "bysource"
autodoc_typehints = "signature"
autodoc_class_signature = "mixed"
autodoc_default_options = {"exclude-members": "__init__, __new__"}
autosummary_generate = False
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_use_rtype = False
napoleon_attr_annotations = True
add_module_names = False
python_use_unqualified_type_names = True

intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}

# Third-party types named in signatures that have no inventory to link to.
nitpick_ignore = [
    ("py:class", "cryptography.hazmat.primitives.asymmetric.ed25519.Ed25519PrivateKey"),
    ("py:class", "cryptography.hazmat.primitives.asymmetric.ed25519.Ed25519PublicKey"),
]

# -- doctest -----------------------------------------------------------------
# Docstring examples run against a small template tree (sphinx-build -b doctest).

doctest_global_setup = """
import os as _os, tempfile as _tempfile
_doctest_cwd = _os.getcwd()
_doctest_dir = _tempfile.mkdtemp(prefix="anza-doctest-")
for _name, _text in {
    "pages/home.html": "<h1>{{title}}</h1>",
    "layout/shell.html": "<html><body>{{content}}</body></html>",
    "feed/card.html": "<article>{{title}}</article>",
}.items():
    _path = _os.path.join(_doctest_dir, "templates", _name)
    _os.makedirs(_os.path.dirname(_path), exist_ok=True)
    with open(_path, "w", encoding="utf-8") as _f:
        _f.write(_text)
_os.chdir(_doctest_dir)
"""
doctest_global_cleanup = """
import shutil as _shutil
_os.chdir(_doctest_cwd)
_shutil.rmtree(_doctest_dir, ignore_errors=True)
"""

# -- HTML: Furo with the Anza palette -----------------------------------------

html_theme = "furo"
html_title = f"anza {release} · Python engine"
html_short_title = "anza for Python"
html_baseurl = "https://anzaui.github.io/py/"
html_logo = "../logo.svg"
html_favicon = "../logo.svg"
templates_path = ["_templates"]
html_static_path = ["_static"]
html_css_files = ["anza.css"]
html_copy_source = False
html_show_sourcelink = False
html_permalinks_icon = "#"
pygments_style = "friendly"
pygments_dark_style = "github-dark"

# Values from anza web/src/tokens/semantic/{light,dark}.css.
_shared = {
    "font-stack": "'Inter', system-ui, -apple-system, sans-serif",
    "font-stack--monospace": "'JetBrains Mono', Consolas, Monaco, 'Ubuntu Mono', monospace",
    "font-stack--headings": "'Plus Jakarta Sans', 'Inter', sans-serif",
}
html_theme_options = {
    "sidebar_hide_name": False,
    "navigation_with_keys": True,
    "top_of_page_buttons": ["view"],
    "source_repository": "https://github.com/anzaui/py/",
    "source_branch": "main",
    "source_directory": "docs/",
    "footer_icons": [
        {
            "name": "GitHub",
            "url": "https://github.com/anzaui/py",
            "html": (
                '<svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 16 16">'
                '<path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17'
                ".55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68"
                "-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64"
                "-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27"
                " 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15"
                " 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013"
                ' 8.013 0 0016 8c0-4.42-3.58-8-8-8z"></path></svg>'
            ),
            "class": "",
        },
    ],
    "light_css_variables": {
        **_shared,
        "color-brand-primary": "#07a45f",
        "color-brand-content": "#076b46",
        "color-brand-visited": "#076b46",
        "color-foreground-primary": "#333333",
        "color-foreground-secondary": "#494d52",
        "color-foreground-muted": "#676c72",
        "color-foreground-border": "#c5c5c5",
        "color-background-primary": "#f6f5ef",
        "color-background-secondary": "#edeee4",
        "color-background-hover": "#e2e4d6",
        "color-background-hover--transparent": "#e2e4d600",
        "color-background-border": "#dfe0d4",
        "color-background-item": "#c5c5c5",
        "color-sidebar-background": "#f6f5ef",
        "color-sidebar-background-border": "#e1e2d6",
        "color-sidebar-link-text": "#676c72",
        "color-sidebar-link-text--top-level": "#3f4246",
        "color-sidebar-item-background--hover": "#e9eadf",
        "color-sidebar-caption-text": "#494d52",
        "color-sidebar-search-background": "#efefe7",
        "color-sidebar-search-background--focus": "#f6f5ef",
        "color-sidebar-search-border": "#e1e2d6",
        "color-toc-item-text": "#676c72",
        "color-toc-item-text--hover": "#1f2937",
        "color-toc-item-text--active": "#07a45f",
        "color-link": "#1565c0",
        "color-link--hover": "#0d47a1",
        "color-link--visited": "#1565c0",
        "color-link-underline": "#1565c000",
        "color-link-underline--hover": "#1565c0",
        "color-code-background": "#edebe9",
        "color-code-foreground": "#383a42",
        "color-inline-code-background": "#edebe9",
        "color-highlighted-background": "#c8f5e3b2",
        "color-highlighted-text": "#054a30",
        "color-header-background": "#f6f5ef",
        "color-header-border": "#e1e2d6",
        "color-header-text": "#1f2937",
        "color-card-background": "#edeee4",
        "color-card-border": "#e1e2d6",
        "color-table-header-background": "#e7e7e7d7",
        "color-table-border": "#dcddd2",
        "color-admonition-background": "#edeee4",
        "color-api-name": "#1f2937",
        "color-api-pre-name": "#676c72",
        "color-api-keyword": "#a626a4",
        "color-highlight-on-target": "#c8f5e36c",
    },
    "dark_css_variables": {
        **_shared,
        "color-brand-primary": "#09d379",
        "color-brand-content": "#52e3a1",
        "color-brand-visited": "#52e3a1",
        "color-foreground-primary": "#eef0f1",
        "color-foreground-secondary": "#c4d2e4",
        "color-foreground-muted": "#7a8860",
        "color-foreground-border": "#3a4428",
        "color-background-primary": "#1d2018",
        "color-background-secondary": "#141a0e",
        "color-background-hover": "#1e2818",
        "color-background-hover--transparent": "#1e281800",
        "color-background-border": "#283018",
        "color-background-item": "#3a4428",
        "color-sidebar-background": "#1d2018",
        "color-sidebar-background-border": "#283018",
        "color-sidebar-link-text": "#dde2e5",
        "color-sidebar-link-text--top-level": "#e1e6ea",
        "color-sidebar-item-background--hover": "#262b1f",
        "color-sidebar-caption-text": "#c4d2e4",
        "color-sidebar-search-background": "#181c13",
        "color-sidebar-search-background--focus": "#141a0e",
        "color-sidebar-search-border": "#283018",
        "color-toc-item-text": "#c4d2e4",
        "color-toc-item-text--hover": "#f6f7f8",
        "color-toc-item-text--active": "#09d379",
        "color-link": "#5aa3dd",
        "color-link--hover": "#8cc2ec",
        "color-link--visited": "#5aa3dd",
        "color-link-underline": "#5aa3dd00",
        "color-link-underline--hover": "#5aa3dd",
        "color-code-background": "#141a0e",
        "color-code-foreground": "#e4ead8",
        "color-inline-code-background": "#2a2e24",
        "color-highlighted-background": "#09d37933",
        "color-highlighted-text": "#e4ead8",
        "color-header-background": "#1d2018",
        "color-header-border": "#283018",
        "color-header-text": "#f6f7f8",
        "color-card-background": "#141a0e",
        "color-card-border": "#283018",
        "color-table-header-background": "#1e2818",
        "color-table-border": "#283018",
        "color-admonition-background": "#141a0e",
        "color-api-name": "#f6f7f8",
        "color-api-pre-name": "#9fb5cf",
        "color-api-keyword": "#cc99cd",
        "color-highlight-on-target": "#07a45f40",
    },
}

# -- Public names ------------------------------------------------------------
# Objects are documented under the names users import (``anza.Engine``), but
# signatures refer to where they are defined (``anza.engine.cache.engine.Engine``).
# Resolve those references to the public name.

_PUBLIC = {name: f"anza.{name}" for name in anza.__all__}


def _public_reference(app, env, node, contnode):
    if node.get("refdomain") != "py":
        return None
    target = node.get("reftarget", "")
    if not target.startswith("anza.") or target in _PUBLIC.values():
        return None
    head, _, last = target.rpartition(".")
    parts = head.split(".")
    # anza.x.y.Class.member -> anza.Class.member
    for i in range(len(parts), 0, -1):
        if parts[i - 1] in _PUBLIC:
            public = ".".join([_PUBLIC[parts[i - 1]], *parts[i:], last])
            break
    else:
        if last not in _PUBLIC:
            return None
        public = _PUBLIC[last]
    domain = env.get_domain("py")
    return domain.resolve_xref(env, node["refdoc"], app.builder, node["reftype"], public, node, contnode)


def _factory_defaults(app, what, name, obj, options, signature, return_annotation):
    # Dataclass ``field(default_factory=...)`` defaults show as ``<factory>``,
    # which is not valid Python and breaks Sphinx's signature parser.
    if signature and "<factory>" in signature:
        return signature.replace("<factory>", "..."), return_annotation
    return None


# Module-level constants re-exported by ``anza``: autodoc looks for their
# ``#:`` comment in ``anza/__init__.py``; read it where they are defined.
_DATA_HOMES = {
    "anza.SignMode": "anza.engine.cache.engine",
    "anza.ENVELOPE_VERSION": "anza.crypto.envelope",
}


def _data_comment(app, what, name, obj, options, lines):
    home = _DATA_HOMES.get(name)
    if what == "data" and home:
        from sphinx.pycode import ModuleAnalyzer

        comment = ModuleAnalyzer.for_module(home).find_attr_docs()[("", name.rpartition(".")[2])]
        lines[:] = [*comment]


def setup(app):
    app.connect("autodoc-process-docstring", _data_comment)
    app.connect("missing-reference", _public_reference)
    app.connect("autodoc-process-signature", _factory_defaults)
