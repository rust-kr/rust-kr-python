# -*- encoding:utf-8 -*-

# SQL Alchemy settings
DB_URI = 'sqlite:///rustkr.db'

SECRET_KEY = '7_Mk_/^6!//`cuG%`+\\8=/ZE3.(BbAa5'

DEBUG = True

CONNECTIONS = [
    {
        'name': 'rustkr',
        'host': 'ocarina.irc.ozinger.org',
        'port': 8080,
        'nick': 'stainless',
        'autojoins': ['#rust'],
        'enabled': True,
        'admin': None,
        'invite': 'disallow',
    }
]

RAW_LOG = False

try:
    from local_settings import *
except ImportError:
    print '*** NO local_settings.py file set up. read README! ***'
    pass

