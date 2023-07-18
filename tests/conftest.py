#  Copyright (c) 2023 Andrii Malchyk, All rights reserved.

import json
from pathlib import Path

import pymongo
import pytest


@pytest.fixture(scope="session")
def database_connect():
    config_json_file_path = Path('../config.json')
    # check if config.json exists
    if config_json_file_path.is_file():
        config_json_file = open(config_json_file_path)
        # try to read json
        config_json = json.loads(config_json_file.read())
        dbstring = config_json['dbstring']
        maxSevSelDelay = 3
        dbserver = pymongo.MongoClient(
            dbstring, serverSelectionTimeoutMS=maxSevSelDelay)
        dbserver.server_info()  # force connection on a request
        yield dbserver['searchmydata']
        dbserver.close()
    else:
        yield None
