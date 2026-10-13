Templates
=========

Templates use ``{{name}}`` placeholders (escaped when the engine runs with
``escape=True``) and ``{{{name}}}`` raw placeholders (never escaped). These
are the parser and binder the engine uses; a :class:`~anza.Template` keeps
the compiled form.

.. currentmodule:: anza

.. autofunction:: extract

.. autofunction:: string

.. autofunction:: escape_html

.. autoclass:: Chunk
   :members:
