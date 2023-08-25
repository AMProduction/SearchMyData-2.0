#  Copyright (c) 2023 Andrii Malchyk, All rights reserved.
import os

from flask import Flask
from flask_wtf.csrf import CSRFProtect
from pymongo import MongoClient
from mongoengine import connect

from config import Config

app = Flask(__name__)
app.config.from_object(Config)

csrf = CSRFProtect(app)
csrf.init_app(app)

mongo = MongoClient(os.getenv('MONGO_URI'))
connect(alias=os.getenv('MONGO_INITDB_DATABASE'), host=os.getenv('MONGO_URI'))

from flaskr import routes
