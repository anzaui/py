"""Response helpers for web frameworks.

The engine itself does not depend on any framework: a :class:`~anza.Document`
is a string of HTML and an :class:`~anza.Envelope` serializes to JSON, so any
framework can send them. These small helpers do it for the common ones. They
import the framework lazily, so ``anza`` never requires it.

=================================  ==============================================
Module                             Helpers
=================================  ==============================================
:mod:`anza.adapters.fastapi`       :func:`~anza.adapters.fastapi.html_response`,
                                   :func:`~anza.adapters.fastapi.json_response`
                                   (FastAPI or Starlette responses)
:mod:`anza.adapters.flask`         :func:`~anza.adapters.flask.html_response`,
                                   :func:`~anza.adapters.flask.json_response`
:mod:`anza.adapters.asgi`          :func:`~anza.adapters.asgi.send_html`,
                                   :func:`~anza.adapters.asgi.send_json`
                                   (raw ASGI ``send``)
:mod:`anza.adapters.wsgi`          :func:`~anza.adapters.wsgi.send_html`,
                                   :func:`~anza.adapters.wsgi.send_json`
                                   (raw WSGI ``start_response``)
=================================  ==============================================

.. rubric:: FastAPI

.. code-block:: python

    from fastapi import FastAPI
    from anza import Fragment, Page, Setup, SignOptions
    from anza.adapters.fastapi import html_response, json_response

    engine = Setup(
        root="./templates",
        signing=SignOptions(mode="hmac", secret=secret),  # 32+ bytes
    ).run()
    app = FastAPI()

    @app.get("/")
    async def home():
        return html_response(Page("/", {"title": "Home"}).run(engine))

    @app.get("/card")
    async def card():
        return json_response(Fragment("feed/card.html", "feed", {"title": "Live"}).run(engine))

.. rubric:: Flask

.. code-block:: python

    from flask import Flask
    from anza import Fragment, Page, Setup
    from anza.adapters.flask import html_response, json_response

    engine = Setup(root="./templates").run()
    app = Flask(__name__)

    @app.route("/")
    def home():
        return html_response(Page("/", {"title": "Flask"}).run(engine))

    @app.route("/card")
    def card():
        return json_response(Fragment("feed/card.html", "feed", {"title": "Item"}).run(engine))

.. rubric:: Raw ASGI and WSGI

.. code-block:: python

    from anza import Page
    from anza.adapters import asgi, wsgi

    async def asgi_app(scope, receive, send):
        await asgi.send_html(send, Page(scope["path"]).run(engine))

    def wsgi_app(environ, start_response):
        return wsgi.send_html(start_response, Page(environ["PATH_INFO"]).run(engine))

An unknown route raises :class:`~anza.AnzaError` (``NOT_FOUND``); map it to a
404 in your framework's error handler.
"""

from . import asgi
from . import wsgi
from . import fastapi
from . import flask

__all__ = ["asgi", "wsgi", "fastapi", "flask"]
