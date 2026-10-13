# Rendering

`Page` renders a full HTML document and `Fragment` renders one template into
a JSON envelope for a slot. Both take a dict or any object as their params.

## Pages

`Page(route, params)` maps the route to a template: `/` → `pages/home.html`,
`/about` and `/about/` → `pages/about.html`. Routes only resolve under
`pages/`. When the page doesn't exist, `pages/index.html` is the catch-all.
Otherwise, or for a malformed route (`..`, `\`, NUL), `Page.run` raises
`AnzaError` with code `NOT_FOUND` and the message `Page not found`.

The page markup is inserted as is (no wrapper element) into
`layout/shell.html` as `{{content}}`. The shell is bound with `params` plus
`content`. When there is no shell, the page goes into a minimal default
document with a `<dock-main>` open shadow root.

## Data Binding

```python
from dataclasses import dataclass
from anza import Page

@dataclass
class UserProfile:
    user_id: str
    user_name: str
    role: str

profile = UserProfile(user_id="usr_102", user_name="Alice", role="Admin")
doc = Page("/profile", profile).run(engine)
```

`{{user_name}}` reads `profile.user_name`. Only public, non-callable attributes
are read: names starting with `_` and methods render as empty. Missing values
and `None` render as empty, booleans as `true` / `false`, integral floats
without `.0`, and dicts, lists and tuples as compact JSON (`{"a":1}`).

## Escaping

By default values are inserted **as is, without HTML escaping**. Escape user
input with `escape_html` before passing it in, or turn on the `escape` option:

```python
from anza import Setup, escape_html

escape_html('<a href="x">Tom & Jerry\'s</a>')
# '&lt;a href=&quot;x&quot;&gt;Tom &amp; Jerry&#39;s&lt;/a&gt;'

engine = Setup(root="./templates", escape=True).run()
```

With `escape=True`, `{{name}}` is HTML-escaped and `{{{name}}}` stays raw. Use
`{{{content}}}` in `layout/shell.html` so the rendered page is not escaped
twice.
