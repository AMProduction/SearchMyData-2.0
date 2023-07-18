#  Copyright (c) 2023 Andrii Malchyk, All rights reserved.
import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or b'\xc2\xb0\x87\xd58D\x13\xc6g\x1d\xf5\x97|\xd5\x01\xf8'
