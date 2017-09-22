
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
import mock
import pdb
import os, sys
import multistructlog
import logging

class MockLogging:
    def debug(self, str):
        return str

class TestMultiStructLog(unittest.TestCase):
    def setUp(self):
        self.logging_config= { 
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

    @mock.patch('multistructlog.logging')
    def test_reload(self, mock_logging):
        logger = multistructlog.create_logger({'version':1, 'foo':'bar'})
        logger0 = multistructlog.create_logger({'version':1, 'foo':'bar'})
        logger2 = multistructlog.create_logger({'version':1, 'foo':'notbar'})
        self.assertEqual(logger, logger0)
        self.assertNotEqual(logger,logger2)

        # "Starting" is only printed once 
        self.assertEqual(mock_logging.StreamHandler.call_count, 2)
    
    @mock.patch('multistructlog.logging')
    def test_level(self, mock_logging):
        logger = multistructlog.create_logger({'version':1, 'foo':'x'})
        logger.info('Test 1')
        logger.debug('Test 2')

        # Default level is INFO
        self.assertEqual(mock_logging.StreamHandler.call_count, 1)

    @mock.patch('multistructlog.logging')
    def test_override_level(self, mock_logging):
        logger = multistructlog.create_logger(self.config, level='DEBUG')

        logger.info('Test 1')
        logger.debug('Test 2')

        self.assertEqual(mock_logging.StreamHandler.call_count, 2)

if __name__ == '__main__':
    unittest.main()
