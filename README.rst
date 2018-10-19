multistructlog
==============

This module is a thin wrapper around Structlog that sets and provides defaults
for sending logs to one or more logging destinations with individual formatting
per destination.

The API consists of a single function: ``create_logger()``.

Args:
   logging_config (dict):    Input to logging.config.dictConfig
   level(logging.loglevel):  Overrides logging level for all loggers (not handlers!)

Returns:
   log: structlog logger object

It can be invoked as follows:

    logging_config = ...

    log = multistructlog.create_logger(config, level=logging.INFO)
    log.info('Entered function', foo='bar')

To create a ``logging_config`` dictionary, see these docs:

 https://docs.python.org/2.7/library/logging.config.html#logging.config.dictConfig
 http://www.structlog.org/en/stable/standard-library.html#rendering-using-structlog-based-formatters-within-logging

There are no required arguments to `create_logger()` - any missing parts of the
config will be filled in with defaults that print structured logs to the
console.

If you don't specify a ``formatters`` section in your config, three will be
created which can be used in handlers:

 - ``json``: renders one JSON dictionary per message
 - ``structured``: prints structured logs with the ``structlog.dev.ConsoleRenderer``
 - ``structured-color``: same as ``structured`` but in color

If you don't specify a ``handlers`` section, a handler will be added that logs
to console with ``logging.StreamHandler`` with format ``structured`` at level
``DEBUG``.

If you don't specify a ``loggers`` section, a default logger (empty string)
will be created with all items in ``handlers`` added to it, with a level of
``NOTSET`` (every level printed).

When setting log level, the higher of ``logging_config['loggers'][*]['level']``
and ``logging_config['handlers'][*]['level']`` is used. The ``level`` parameter
overrides the ``loggers`` value of level, not the ``handlers`` one.

If the handler's level is set to ``DEBUG`` but the logger's level is set to
``ERROR``, the handler will only log ``ERROR`` level messages.

Multistructlog also adds a ``TRACE`` log level (integer level 5) that is below
"DEBUG" to both standard library ``Logger`` and Structlog ``BoundLogger``.

List of standard logging levels:
 https://docs.python.org/2.7/library/logging.html#logging-levels
