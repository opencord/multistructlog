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

from six import iteritems
import copy
import logging
import logging.config
import structlog

"""
We expose the Structlog logging interface directly.

This should allow callers to bind contexts incrementally and configure and use
other features of structlog directly.

To create a logging_config dictionary see these docs:

 https://docs.python.org/2.7/library/logging.config.html#logging.config.dictConfig
 http://www.structlog.org/en/stable/standard-library.html#rendering-using-structlog-based-formatters-within-logging

When setting log level, the higher of logging_config['logger'][*]['level'] and
logging_config['handler'][*]['level'] is used.

If the handler's level is set to "DEBUG" but the handler's is set to "ERROR",
the handler will only log "ERROR" level messages.

List of logging levels:
 https://docs.python.org/2.7/library/logging.html#logging-levels

"""

# Add a TRACE log level to both structlog and normal python logger

# new level is 5, per these locations:
# https://github.com/python/cpython/blob/2.7/Lib/logging/__init__.py#L132
# https://github.com/hynek/structlog/blob/18.2.0/src/structlog/stdlib.py#L296
structlog.stdlib.TRACE = TRACE_LOGLVL = 5
structlog.stdlib._NAME_TO_LEVEL['trace'] = TRACE_LOGLVL
logging.addLevelName(TRACE_LOGLVL, "TRACE")


# Create structlog TRACE level and add to BoundLogger object
#  https://github.com/hynek/structlog/blob/18.2.0/src/structlog/stdlib.py#L59
def trace_structlog(self, event=None, *args, **kw):
    ''' enable TRACE for structlog '''
    return self._proxy_to_logger("trace", event, *args, **kw)


structlog.stdlib.BoundLogger.trace = trace_structlog


# create standard logger TRACE level and add to Logger object
#  https://github.com/python/cpython/blob/2.7/Lib/logging/__init__.py#L1152
def trace_loglevel(self, message, *args, **kws):
    ''' enable TRACE for standard logger'''
    if self.isEnabledFor(TRACE_LOGLVL):
        self._log(TRACE_LOGLVL, message, args, **kws)


logging.Logger.trace = trace_loglevel

# used to return same logger on multiple calls without reconfiguring it
# may be somewhat redundant with "cache_logger_on_first_use" in structlog
CURRENT_LOGGER = None
CURRENT_LOGGER_PARAMS = None


def create_logger(logging_config=None, level=None):
    """
    Args:
        logging_config (dict):    Input to logging.config.dictConfig
        level(logging.loglevel):  Overrides logging level for all loggers

    Returns:
        log: structlog logger
    """

    global CURRENT_LOGGER
    global CURRENT_LOGGER_PARAMS

    # if config provided, copy to prevent changes to dict from being pushed
    # back to caller, otherwise use default config
    if logging_config:
        logging_config = copy.deepcopy(logging_config)
    else:
        logging_config = {'version': 1, "disable_existing_loggers": False}

    if CURRENT_LOGGER and CURRENT_LOGGER_PARAMS == (logging_config, level):
        return CURRENT_LOGGER

    # store unmodified config, which is changed later
    CURRENT_LOGGER_PARAMS = (copy.deepcopy(logging_config), level)

    # check if formatters exists in logging_config, set defaults if not set
    if "formatters" not in logging_config:

        logging_config['formatters'] = {
            'json': {
                '()': structlog.stdlib.ProcessorFormatter,
                "processor": structlog.processors.JSONRenderer(),
            },
            'structured-color': {
                '()': structlog.stdlib.ProcessorFormatter,
                'processor': structlog.dev.ConsoleRenderer(colors=True,
                                                           force_colors=True),
            },
            'structured': {
                '()': structlog.stdlib.ProcessorFormatter,
                'processor': structlog.dev.ConsoleRenderer(colors=False),
            },
        }

    # set a default colored output to console handler if none are set
    if "handlers" not in logging_config:

        logging_config['handlers'] = {
            'default': {
                'class': 'logging.StreamHandler',
                'level': 'DEBUG',
            },
        }

    # if a formatter isn't set in a handler, use structured formatter
    for k, v in iteritems(logging_config['handlers']):
        if 'formatter' not in v:
            v['formatter'] = 'structured'

    # add loggers if they don't exist or default '' logger is missing
    if "loggers" not in logging_config or '' not in logging_config['loggers']:

        # By default, include all handlers in default '' logger
        handler_l = logging_config['handlers'].keys()

        logging_config['loggers'] = {
            '': {
                'handlers': handler_l,
                'level': 'NOTSET',  # don't filter on level in logger
                'propagate': True
            },
        }

    # If level is set, override log level of base loggers
    if level:
        for k, v in iteritems(logging_config['loggers']):
            v['level'] = level

    # configure standard logger
    logging.config.dictConfig(logging_config)

    # configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    log = structlog.get_logger()

    CURRENT_LOGGER = log

    return log
