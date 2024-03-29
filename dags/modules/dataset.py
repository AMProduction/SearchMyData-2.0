#  Copyright (c) 2023 Andrii Malchyk, All rights reserved.

import logging
from datetime import datetime
from functools import wraps

import pymongo
from pymongo.errors import ServerSelectionTimeoutError


def measure_execution_time(func):
    """A service function / a decorator to measure up execution time
    """

    @wraps(func)
    def log_time(*args, **kwargs):
        start_time = datetime.now()
        try:
            return func(*args, **kwargs)
        finally:
            end_time = datetime.now()
            logging.info(
                    f'Total execution time {args[0].__class__.__name__}.{func.__name__}: {end_time - start_time}')

    return log_time


class Dataset:
    """Base parent class for all datasets

    --------
    Methods:
    --------
        get_dataset():
            Get the link to the dataset. Return the link to the dataset's source file
        save_dataset():
            Save the dataset into the Database. Input parameter - the link to the dataset's source file.
        clear_collection():
            Purge the collection
        __create_service_json():
            Create and save a JSON with service information about a dataset
        __update_service_json():
            Update and save a JSON with service information about a dataset
        update_metadata():
            Call __create_service_json() if a dataset is first time saved. Or call __update_service_json() if a dataset refreshed
        delete_collection_index():
            Drop a database full-text search index
        create_collection_index():
            Create a database full-text search index
        setup_dataset():
            A sequence of class methods to setup a dataset
        is_collection_exists():
            Check if a collection exists. Input parameter - a collection name
    """

    def __init__(self, connection_string: str, package_base_url: str, resource_base_url: str, package_resource_id: str):
        self.logger = logging.getLogger(__name__)
        self.package_base_url = package_base_url
        self.resource_base_url = resource_base_url
        self.package_resource_id = package_resource_id
        self.__dbstring = connection_string
        try:
            # Set server Selection Timeout in ms. The default value is 30s.
            maxSevSelDelay = 3
            self.dbserver = pymongo.MongoClient(self.__dbstring, serverSelectionTimeoutMS=maxSevSelDelay)
            self.dbserver.server_info()  # force connection on a request
        except ServerSelectionTimeoutError as e:
            logging.error(f'{self.__class__.__name__}: Connection error. {e}')
        else:
            self.db = self.dbserver['searchmydata']
            logging.warning('Connected to DB')
            self.service_col = self.db['ServiceCollection']

    def setup_dataset(self):
        """A sequence of class methods to setup a dataset
        """
        pass

    def __delete_collection_index(self):
        """Drop a database full-text search index
        """
        pass

    def __clear_collection(self):
        """Purge the collection
        """
        pass

    def __get_dataset(self):
        """Get the link to the dataset.
        Return the link to the dataset's source file
        """
        pass

    def __save_dataset(self):
        """Save the dataset into the Database.
        Input parameter - the link to the dataset's source file.
        """
        pass

    def __update_metadata(self):
        """Call __create_service_json() if a dataset is first time saved. Or call __update_service_json() if a dataset refreshed
        """
        pass

    def __update_service_json(self):
        """Update and save a JSON with service information about a dataset
        """
        pass

    def __create_service_json(self):
        """Create and save a JSON with service information about a dataset
        """
        pass

    def __create_collection_index(self):
        """Create a database full-text search index
        """
        pass

    def is_collection_exists(self, collection_name):
        """Check if a collection exists.

        :param collection_name: str/a collection name
        :return: True - if a collection exists; False - if not
        """
        collections_list = self.db.list_collection_names()
        return collection_name in collections_list
