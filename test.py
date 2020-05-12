#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
test.py
(C) 2020 by Damir Cavar <damir@semiring.com>, Semiring Inc.

To run the server with the default port and host, just run this script in the current folder.

The default post is 5000, the default host is localhost.
"""

from flask import Flask
from japi import app

## install benepar this is just for the first time when the user sets up the api 
import benepar
benepar.download('benepar_en2')

app.debug = True

if __name__ == "__main__":
    app.run()

