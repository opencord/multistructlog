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

import unittest
import multistructlog

# mock imports differently in python 3
try:
    import mock
except ImportError:
    import unittest.mock as mock


class TestMultiStructLog(unittest.TestCase):

    def setUp(self):
        self.logging_config = {
            'version': 1,
            'handlers': {
                'default': {
                    'class': 'logging.StreamHandler',
                },
            },

            'loggers': {
                '': {
                    'handlers': ['default'],
                    'level': 'INFO',
                    'propagate': True
                },
            }
        }

        self.config = self.logging_config

    def test_reload(self):
        '''
        Test that creating creatinging multiple identical loggers will reuse
        existing loggers
        '''

        logger = multistructlog.create_logger({'version': 1, 'foo': 'bar'})
        logger0 = multistructlog.create_logger({'version': 1, 'foo': 'bar'})
        logger2 = multistructlog.create_logger({'version': 1, 'foo': 'notbar'})

        self.assertEqual(logger, logger0)
        self.assertNotEqual(logger, logger2)

    @mock.patch('logging.Logger.handle')
    def test_level(self, mocked):
        '''
        Default level is INFO, so Logger.handle will only be called once
        '''

        logger = multistructlog.create_logger(self.config)

        logger.info('Test 1')
        logger.debug('Test 2')

        self.assertEqual(mocked.call_count, 1)

    @mock.patch('logging.Logger.handle')
    def test_override_level(self, mocked):
        '''
        level changed to DEBUG, so Logger.handle will be called twice
        '''

        logger = multistructlog.create_logger(self.config, level='DEBUG')

        logger.info('Test 1')
        logger.debug('Test 2')

        self.assertEqual(mocked.call_count, 2)
