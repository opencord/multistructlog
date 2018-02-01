# Copyright 2017-present Open Networking Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
multistructlog logging module

This module enables structured data to be logged to a single destination, or to
multiple destinations simulataneously.  The API consists of a single function:
create_logger, which returns a structlog object. You can invoke it as follows:

    log = logger.create_logger(xos_config, level=logging.INFO)
    log.info('Entered function', name = '%s' % fn_name)

The default handlers in XOS are the console and Logstash. You can override the
handlers, structlog's processors, or anything else by adding keyword arguments
to create_logger:

    log = logger.create_logger(xos_config, level=logging.INFO,
		 	       handlers=[logging.StreamHandler(sys.stdout),
					 logstash.LogstashHandler('somehost', 5617, version=1)])

Each handler depends on a specific renderer (e.g. Logstash needs JSON and
stdout needs ConsoleRenderer) but a structlog instance can enchain only one
renderer. For this reason, we apply renderers at the logging layer, as
logging formatters.
"""

import logging
import logging.config
import logstash
import structlog
import sys
import copy
import inspect

PROCESSOR_MAP = {
    'StreamHandler': structlog.dev.ConsoleRenderer(colors=True, force_colors=True),
    'LogstashHandler': structlog.processors.JSONRenderer(),
    'RotatingFileHandler': structlog.processors.JSONRenderer()
}


class FormatterFactory:
    def __init__(self, handler_name):
        self.handler_name = handler_name

    def __call__(self):
        try:
            processor = PROCESSOR_MAP[self.handler_name]
        except KeyError:
            processor = structlog.processors.KeyValueRenderer()

        formatter = structlog.stdlib.ProcessorFormatter(processor)

        return formatter


class XOSLoggerFactory:
    def __init__(self, handlers):
        self.handlers = handlers

    def __call__(self):
        base_logger = logging.getLogger("multistructlog")
        base_logger.handlers = []
        for h in self.handlers:
            formatter = FormatterFactory(h.__class__.__name__)()
            h.setFormatter(formatter)
            base_logger.addHandler(h)

        self.logger = base_logger
        return self.logger


""" We expose the Structlog logging interface directly. This should allow callers to
    bind contexts incrementally and configure and use other features of structlog directly

    The use of structlog in Chameleon was used for reference when writing this code.
"""

CURRENT_LOGGER = None
CURRENT_LOGGER_PARMS = None


def create_logger(_config=None, extra_processors=[],
                  force_create=False, level=None):
    """
    Args:
        _config (dict): 		The standard config for Python's logging module
        extra_processors(dict): 	Custom structlog processors
        force_create(bool): 		Forces creation of the logger
        level(logging.loglevel): 	Overrides logging level

    Returns:
        log: structlog logger
    """

    first_entry_elts = ['Starting']

    """Inherit base options from config"""
    if _config:
        logging_config = copy.deepcopy(_config)
    else:
        first_entry_elts.append('Config is empty')
        logging_config = {'version': 1}

    """Check if a logger with this configuration has already been created, if so, return that logger
       instead of creating a new one"""
    global CURRENT_LOGGER
    global CURRENT_LOGGER_PARMS
    if CURRENT_LOGGER and CURRENT_LOGGER_PARMS == (
            logging_config, extra_processors, level) and not force_create:
        return CURRENT_LOGGER

    if level:
        try:
            for k, v in logging_config['loggers'].iteritems():
                v['level'] = level
        except KeyError:
            first_entry_elts.append('Level override failed')

    logging.config.dictConfig(logging_config)

    processors = copy.copy(extra_processors)
    processors.extend([
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter
    ])

    
    handlers = logging.getLogger('multistructlog').handlers

    if not handlers:
        caller = inspect.stack()[1]

        try:
            filename = inspect.getmodule(caller[0]).__name__
        except AttributeError:
            filename = '/tmp/multistructlog'

        handlers = [
            logging.StreamHandler(sys.stdout),
            logging.handlers.RotatingFileHandler(
                filename=filename,
                maxBytes=10485760,
                backupCount=1)
        ]

    factory = XOSLoggerFactory(handlers)

    structlog.configure(
        processors=processors,
        logger_factory=factory,
    )

    log = structlog.get_logger()
    first_entry = '. '.join(first_entry_elts)
    log.info(first_entry, level_override=level, **logging_config)

    CURRENT_LOGGER = log
    CURRENT_LOGGER_PARMS = (logging_config, extra_processors, level)
    return log


if __name__ == '__main__':
    l = create_logger(
        {'version': 2, 'loggers': {'': {'level': 'INFO'}}}, level="INFO")
    l.info("Test OK")
