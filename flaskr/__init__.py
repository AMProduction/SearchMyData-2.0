#  Copyright (c) 2023 Andrii Malchyk, All rights reserved.
from flask import Flask

from config import Config

app = Flask(__name__)
app.config.from_object(Config)

from flaskr import routes
