multistructlog
==============

This module is a thin wrapper around structlog that sets and provides defaults
for multiple logging destinations.


The API consists of a single function: create_logger

Args:
   logging_config (dict):    Input to logging.config.dictConfig
   level(logging.loglevel):  Overrides logging level for all loggers (not handlers!)

Returns:
   log: structlog logger object

It can be invoked it as follows:

    logging_config = ...

    log = multistructlog.create_logger(config, level=logging.INFO)
    log.info('Entered function', name = '%s' % fn_name)

You don't need to supply a config - by default missing parts of the config will
be filled in with defaults that print structured logs to the console.

if you don't specify a formatters in your config, 3 will be created which can
be used in handlers:

 - json, which renders one JSON dictionary per message
 - structured, which prints structured logs with the structlog.dev.ConsoleRendered
 - structured-color, same as above but in color

To create a logging_config dictionary see these docs:

 https://docs.python.org/2.7/library/logging.config.html#logging.config.dictConfig
 http://www.structlog.org/en/stable/standard-library.html#rendering-using-structlog-based-formatters-within-logging

When setting log level, the higher of logging_config['loggers'][*]['level'] and
logging_config['handlers'][*]['level'] is used. The 'level' parameter overrides
the 'loggers' value of level, not the 'handlers' one.

If the handler's level is set to "DEBUG" but the logger's is set to "ERROR",
the handler will only log "ERROR" level messages.

List of logging levels:
 https://docs.python.org/2.7/library/logging.html#logging-levels

