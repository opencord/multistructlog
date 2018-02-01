#!/usr/bin/env python
#
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

from setuptools import setup

setup(name='multistructlog',
      version='1.5',
      description='structlog with multiple simultaneous logging backends',
      author='Varun Belur, Sapan Bhatia',
      author_email='varun@opennetworking.org,sapan@opennetworking.org',
      py_modules=['multistructlog'],
      license='Apache 2',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'Topic :: System :: Logging',
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python :: 2.7'
      ],
      copyright='Open Networking Foundation',
      include_package_data=True,
      install_requires=['structlog', 'python-logstash', 'colorama'],
      keywords=['multistructlog', 'structlog',
                'multiple backends', 'xos logging']
      )
