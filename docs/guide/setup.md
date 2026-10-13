# Setup Options

`Setup(...)` describes where the templates are and how to render and sign
them. `run()` loads and parses every template under `root` once and returns
the `Engine` that `Page`, `Fragment` and `Stream` use.

```python
engine = Setup(
    root="./templates",
    signing=SignOptions(mode="hmac", secret=secret),
    fragments=["feed/", "partials/menu.html"],  # fragment allowlist
    escape=True,                                # escape {{x}}, keep {{{x}}} raw
    max_template_bytes=512 * 1024,              # default 1 MiB
    watch=True,                                 # reload on change
).run()

engine.close()  # stops the watcher
```

- `fragments` limits which templates `Fragment` can render. An entry ending in
  `/` allows that prefix and any other entry allows that exact name. Anything
  else is reported as `Template '<name>' not found`. Empty (the default)
  allows every template.
- `max_template_bytes` makes a larger file a `TEMPLATE` error at load.
- `watch=True` starts a polling thread that reloads the templates when files
  are added, changed or removed. Stop it with `engine.close()`.

Template names are relative `/`-separated paths (no leading `/`, `\`, NUL,
or empty, `.` or `..` segments). A malformed name is a `VALIDATION` error.
Lookups only use the templates loaded at setup: a cache miss is `NOT_FOUND`
and never reads from disk.
