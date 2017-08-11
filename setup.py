#!/usr/bin/env python

from setuptools import setup

setup(name='multistructlog',
      version='1.0',
      description='structlog with multiple simultaneous logging backends',
      author='Varun Belur, Sapan Bhatia',
      author_email='varun@opennetworking.org,sapan@opennetworking.org',
      py_modules=['multistructlog'],
      license='Apache 2',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'Intended Audience :: Telecommunications Industry'
          'Topic :: System :: Logging',
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python :: 2.7'
      ],     
      copyright='Open Networking Foundation',
      include_package_data=True,
      install_requires=['structlog', 'logstash', 'colorama'],
      keywords=['multistructlog', 'structlog', 'multiple backends', 'xos logging']
     )
