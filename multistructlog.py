# What is a version... Version of our logger? Version of logging library? Version of the module?
# log.msg doesn't work. It ought to work.
# Try loading an existing config file into a logger, try variations, overriding defaults

import logging
import logging.config
import logstash
import structlog
import sys
import pdb
import copy


PROCESSOR_MAP = {
        'StreamHandler': structlog.dev.ConsoleRenderer(),
        'LogstashHandler': structlog.processors.JSONRenderer(),
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
        base_logger = logging.getLogger()
        for h in self.handlers:
            formatter = FormatterFactory(h.__class__.__name__) ()
            h.setFormatter(formatter)
            base_logger.addHandler(h)

        self.logger = base_logger
        return self.logger

""" We expose the Structlog logging interface directly. This should allow callers to
    bind contexts incrementally and configure and use other features of structlog directly 

    - config is the root xos configuration
    - overrides override elements of that config, e.g. level=logging.INFO would cause debug messages to be dropped
    - overrides can contain a 'processors' element, which lets you add processors to structlogs chain 

    The strategy to expose structlog directly was inspired by Chameleon
"""
def create_logger(_config, **overrides):
    first_entry_elts = ['Starting']
    first_entry_struct = {}

    """Inherit base options from config"""
    try:
        logging_config = copy.deepcopy(_config.get('logging'))
    except AttributeError:
        first_entry_elts.append('Config is empty')
        logging_config = {}

    if overrides:
        first_entry_struct['overrides'] = overrides

    for k,v in overrides.items():
        logging_config[k] = v

    default_handlers = [
        logging.StreamHandler(sys.stdout),
        #logstash.LogstashHandler('localhost', 5617, version=1)
    ]

    handlers = logging_config.get('handlers', default_handlers)
    logging.config.dictConfig(logging_config)

    # Processors
    processors = overrides.get('processors', [])

    processors.extend([
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter
    ])

    factory = XOSLoggerFactory(handlers)

    structlog.configure(
            processors=processors,
            logger_factory=factory,
        )

    log = structlog.get_logger()
    first_entry = '. '.join(first_entry_elts)
    log.info(first_entry, **first_entry_struct)

    return log
