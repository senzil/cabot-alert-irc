#!/usr/bin/env python

from setuptools import setup

setup(name='cabot-alert-irc',
      version='1.1.0',
      description='An IRC alert plugin for Cabot by Arachnys',
      author='nobe4',
      author_email='vh@nobe4.fr',
      license='MIT',
      url='http://cabotapp.com',
      packages=['cabot_alert_irc'],
      install_requires=['irc3'],
     )
