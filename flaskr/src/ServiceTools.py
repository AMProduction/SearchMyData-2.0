import json
import logging
import os
from pathlib import Path
from datetime import datetime, timedelta

import pymongo
from prettytable import PrettyTable
from pymongo.errors import ServerSelectionTimeoutError


class ServiceTools:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.__configJsonFilePath = Path('config.json')
        # check if config.json exists
        if self.__configJsonFilePath.is_file():
            logging.warning(f'{self.__class__.__name__}: Config.json is found')
            self.__configJsonFile = open(self.__configJsonFilePath)
            # try to read json
            try:
                self.__configJson = json.loads(self.__configJsonFile.read())
            except ValueError:
                logging.error(
                    f'{self.__class__.__name__}: Config.json format error')
            # read db connection string
            try:
                self.__dbstring = self.__configJson['dbstring']
            except KeyError:
                logging.error(
                    f'{self.__class__.__name__}: "dbstring" key is not found in Config.json')
            # try to connect
            try:
                # Set server Selection Timeout in ms. The default value is 30s.
                maxSevSelDelay = 3
                self.__dbserver = pymongo.MongoClient(
                    self.__dbstring, serverSelectionTimeoutMS=maxSevSelDelay)
                self.__dbserver.server_info()  # force connection on a request
            except ServerSelectionTimeoutError:
                logging.error(f'{self.__class__.__name__}: Connection error')
            else:
                self.__db = self.__dbserver["searchmydata"]
                self.__serviceCol = self.__db['ServiceCollection']
        # if config.json does not exists
        else:
            logging.error(
                f'{self.__class__.__name__}: Config.json is not found')

    def getRegistersInfo(self):
        result = self.__serviceCol.find({}, {'_id': 1, 'Description': 1, 'DocumentsCount': 1, 'LastModifiedDate': 1}).sort([('_id', 1)])
        return result

    def checkIsExpired(self):
        isExpired = False
        expiredTime = datetime.now() - timedelta(days=2)
        for record in self.__serviceCol.find():
            lastModifiedDate = datetime.strptime(
                record['LastModifiedDate'], '%Y-%m-%d %H:%M:%S.%f')
            if lastModifiedDate < expiredTime:
                logging.warning(record['Description'] + ' is out of date')
                isExpired = True
        return isExpired