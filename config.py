#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Configuration file """

import json
from dotenv import load_dotenv
import os

#db params
load_dotenv()
db_host = os.getenv("DATABASE_HOST")
db_name = os.getenv("DATABASE_NAME")
db_user = os.getenv("DATABASE_USER")
db_password = os.getenv("DATABASE_PASSWORD")
