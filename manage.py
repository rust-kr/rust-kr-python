#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from flask import Flask
from flaskext.actions import Manager
import settings
from rustkr import app

app.config.from_object(settings)
manager = Manager(app)

if __name__ == "__main__":
    manager.run()

