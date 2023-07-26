#  Copyright (c) 2023 Andrii Malchyk, All rights reserved.

import gc
import json
import logging
from datetime import datetime

import requests
from pymongo.errors import PyMongoError

from .dataset import Dataset, measure_execution_time


class MissingPersonsRegister(Dataset):
    def __init__(self, connection_string, package_base_url, resource_base_url, package_resource_id):
        super().__init__(connection_string, package_base_url, resource_base_url, package_resource_id)

    @measure_execution_time
    def setup_dataset(self):
        self.__delete_collection_index()
        self.__clear_collection()
        __dataset = self.__get_dataset()
        self.__save_dataset(__dataset)
        self.__update_metadata()
        self.__create_collection_index()

    @measure_execution_time
    def __delete_collection_index(self):
        if self.is_collection_exists('MissingPersons'):
            missing_persons_col = self.db['MissingPersons']
            if 'full_text' in missing_persons_col.index_information():
                missing_persons_col.drop_index('full_text')
                logging.warning('Missing persons Text index deleted')

    @measure_execution_time
    def __clear_collection(self):
        if self.is_collection_exists('MissingPersons'):
            missing_persons_col = self.db['MissingPersons']
            count_deleted_documents = missing_persons_col.delete_many({})
            logging.warning(f'{count_deleted_documents.deleted_count} documents deleted. The missing persons '
                            f'collection is empty.')

    @measure_execution_time
    def __get_dataset(self):
        try:
            general_dataset = requests.get(self.package_base_url + self.package_resource_id).text
        except ConnectionError as e:
            logging.error(f'Error during general MissingPersons dataset JSON receiving occurred: {e}')
        else:
            general_dataset_json = json.loads(general_dataset)
            logging.info('A general MissingPersons dataset JSON received')
        # get dataset id
        missing_persons_general_dataset_id = general_dataset_json['result']['resources'][0]['id']
        try:
            # get resources JSON id
            missing_persons_general_dataset_id_json = requests.get(
                    self.resource_base_url + missing_persons_general_dataset_id).text
        except ConnectionError as e:
            logging.error(f'Error during MissingPersons resources JSON id receiving occurred: {e}')
        else:
            missing_persons_general_dataset_json = json.loads(missing_persons_general_dataset_id_json)
            logging.info('A MissingPersons resources JSON id received')
        # get dataset json url
        missing_persons_dataset_json_url = missing_persons_general_dataset_json['result']['url']
        try:
            # get dataset
            missing_persons_dataset_json = requests.get(missing_persons_dataset_json_url).text
        except ConnectionError as e:
            logging.error(f'Error during MissingPersons dataset receiving occurred {e}')
        else:
            missing_persons_dataset = json.loads(missing_persons_dataset_json)
            logging.info('A MissingPersons dataset received')
        return missing_persons_dataset

    @measure_execution_time
    def __save_dataset(self, json):
        missing_persons_col = self.db['MissingPersons']
        try:
            missing_persons_col.insert_many(json)
        except PyMongoError as e:
            logging.error(f'Error during saving Missing Persons Register into Database: {e}')
        else:
            logging.info('Missing persons dataset was saved into the database')
        gc.collect()

    @measure_execution_time
    def __update_metadata(self):
        # update or create MissingPersonsRegisterServiceJson
        if (self.is_collection_exists('ServiceCollection')) and (
                self.service_col.count_documents({'_id': 1}, limit=1) != 0):
            self.__update_service_json()
            logging.info('MissingPersonsRegisterServiceJson updated')
        else:
            self.__create_service_json()
            logging.info('MissingPersonsRegisterServiceJson created')

    @measure_execution_time
    def __update_service_json(self):
        last_modified_date = datetime.now()
        missing_persons_col = self.db['MissingPersons']
        documents_count = missing_persons_col.count_documents({})
        self.service_col.update_one(
                {'_id': 1},
                {'$set': {'LastModifiedDate': str(last_modified_date),
                          'DocumentsCount': documents_count}}
        )

    @measure_execution_time
    def __create_service_json(self):
        created_date = datetime.now()
        last_modified_date = datetime.now()
        missing_persons_col = self.db['MissingPersons']
        documents_count = missing_persons_col.count_documents({})
        missing_persons_register_service_json = {
                '_id': 1,
                'Description': 'Інформація про безвісно зниклих громадян',
                'DocumentsCount': documents_count,
                'CreatedDate': str(created_date),
                'LastModifiedDate': str(last_modified_date)
        }
        self.service_col.insert_one(missing_persons_register_service_json)

    @measure_execution_time
    def __create_collection_index(self):
        missing_persons_col = self.db['MissingPersons']
        missing_persons_col.create_index(
                [('FIRST_NAME_U', 'text'), ('LAST_NAME_U', 'text'), ('MIDDLE_NAME_U', 'text')], name='full_text')
        logging.info('Missing persons Text Index created')
