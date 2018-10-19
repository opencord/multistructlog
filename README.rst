multistructlog
==============

This module enables structured data to be logged to a single destination, or to
multiple destinations simulataneously.  The API consists of a single function:
create_logger, which returns a structlog object.

It canb be invoked it as follows:

    config = ...

    log = logger.create_logger(config, level=logging.INFO)
    log.info('Entered function', name = '%s' % fn_name)

You can override the handlers, structlog's processors, or anything else by
adding keyword arguments to create_logger:

    log = logger.create_logger(xos_config, level=logging.INFO,
                               handlers=[logging.StreamHandler(sys.stdout),
                                         logstash.LogstashHandler('somehost', 5617, version=1)])

Each handler depends on a specific renderer (e.g. Logstash needs JSON and
stdout needs ConsoleRenderer) but a structlog instance can enchain only one
renderer. For this reason, we apply renderers at the logging layer, as logging
formatters.
