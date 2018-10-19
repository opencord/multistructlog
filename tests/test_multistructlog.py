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

import multistructlog
import os
import logging
import logging.config
import shutil
import json
import unittest
import structlog

# test directory, cleared and left around after testing
test_scratch = "msl_test_scratch"


class TestMultiStructLog(unittest.TestCase):

    @classmethod
    def setUpClass(clsG):
        # delete and recreate test_scratch directory if it exists
        if os.path.isdir(test_scratch):
            shutil.rmtree(test_scratch)

        os.mkdir(test_scratch)

    def tearDown(self):
        structlog.reset_defaults()

    def test_reload(self):
        '''
        Test that creating creatinging multiple identical loggers will reuse
        existing loggers
        '''

        logger0 = multistructlog.create_logger({'version': 1, 'foo': 'bar'})
        logger1 = multistructlog.create_logger({'version': 1, 'foo': 'bar'})
        logger2 = multistructlog.create_logger()

        self.assertEqual(logger0, logger1)
        self.assertNotEqual(logger0, logger2)

    def test_different_formatters(self):
        '''
        Test different formattters and levels to different output streams
        NOTE: Only one test as logger has global state that is hard to reset
        between tests without breaking other things.
        '''

        f1 = os.path.join(test_scratch, 'different_formatters_test_file1')
        f2 = os.path.join(test_scratch, 'different_formatters_test_file2.json')

        logging_config = {
            'version': 1,
            'handlers': {
                'file1': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'level': 'WARNING',
                    'formatter': 'structured',
                    'filename': f1,
                },
                'file2': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'level': 'INFO',
                    'formatter': 'json',
                    'filename': f2,
                },
            },
            'formatters': {
                'json': {
                    '()': structlog.stdlib.ProcessorFormatter,
                    "processor": structlog.processors.JSONRenderer(),
                },
                'structured': {
                    '()': structlog.stdlib.ProcessorFormatter,
                    'processor': structlog.dev.ConsoleRenderer(colors=False),
                },
            },
            'loggers': {
                '': {
                    'handlers': ['file1', 'file2'],
                    'level': 'WARNING',
                    'propagate': True
                },
            }
        }

        # reset level to debug, overriding 'loggers' directive above
        logger = multistructlog.create_logger(logging_config,
                                              level=logging.DEBUG)

        extra_data = {'number': 42}

        logger.warning("should be in both files", extra=extra_data)

        # filtered by file1 handler
        logger.info("should only be in file2")

        # filtered by both handlers, but not by loggers
        logger.debug("should not be in either file")

        # test new trace level
        logger.trace("testing trace, shouldn't be in either file")

        # check contents of file1
        with open(f1) as f1fh:
            f1_desired = '''should be in both files        extra={'number': 42}
'''
            self.assertEqual(f1fh.read(), f1_desired)

        # check contents of file2
        f2_read = []
        f2_desired = [
            {"event": "should be in both files", "extra": {"number": 42}},
            {"event": "should only be in file2"},
        ]

        with open(f2) as f2fh:
            for line in f2fh:
                f2_read.append(json.loads(line))

        self.assertEqual(f2_read, f2_desired)
