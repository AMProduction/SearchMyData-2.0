#  Copyright (c) 2023 Andrii Malchyk, All rights reserved.

import logging
from datetime import datetime, timedelta

import pymongo
from pymongo.errors import ServerSelectionTimeoutError


class ServiceTools:
    """Class for service purpose

    --------
    Methods:
    --------
          get_registers_info():
            Show the list of available registers, count of documents, and the last update date
          check_is_expired():
            Check if a dataset last updated date is older than 2 days ago
    """

    def __init__(self, connection_string: str):
        self.logger = logging.getLogger(__name__)
        self.__dbstring = connection_string
        # try to connect
        try:
            # Set server Selection Timeout in ms. The default value is 30s.
            maxSevSelDelay = 3
            self.__dbserver = pymongo.MongoClient(self.__dbstring, serverSelectionTimeoutMS=maxSevSelDelay)
            self.__dbserver.server_info()  # force connection on a request
        except ServerSelectionTimeoutError:
            logging.error(f'{self.__class__.__name__}: Connection error')
        else:
            self.__db = self.__dbserver["searchmydata"]
            self.__serviceCol = self.__db['ServiceCollection']

    def get_registers_info(self):
        """Show the list of available registers, count of documents, and the last update date
                """
        result = self.__serviceCol.find({}, {'_id': 1, 'Description': 1, 'DocumentsCount': 1, 'LastModifiedDate': 1}) \
            .sort([('_id', 1)])
        return result

    def check_is_expired(self):
        """Check if a dataset last updated date is older than 2 days ago
        """
        is_expired = False
        expired_time = datetime.now() - timedelta(days=2)
        for record in self.__serviceCol.find():
            last_modified_date = datetime.strptime(record['LastModifiedDate'], '%Y-%m-%d %H:%M:%S.%f')
            if last_modified_date < expired_time:
                logging.warning(f'{record["Description"]} is out of date')
                is_expired = True
        return is_expired
