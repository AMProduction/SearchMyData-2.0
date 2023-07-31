#  Copyright (c) 2023 Andrii Malchyk, All rights reserved.
import os

from flask import Flask
from pymongo import MongoClient

from config import Config

app = Flask(__name__)
app.config.from_object(Config)

mongo = MongoClient(os.getenv('MONGO_URI'))

from flaskr import routes
