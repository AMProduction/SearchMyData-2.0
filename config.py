#  Copyright (c) 2023 Andrii Malchyk, All rights reserved.
import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
