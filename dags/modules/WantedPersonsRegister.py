#  Copyright (c) 2023 Andrii Malchyk, All rights reserved.

import gc
import json
import logging
from datetime import datetime

import requests
from pymongo.errors import PyMongoError

from .dataset import Dataset


class WantedPersonsRegister(Dataset):
    def __init__(self, connection_string):
        super().__init__(connection_string)

    @Dataset.measure_execution_time
    def __get_dataset(self):
        try:
            general_dataset = requests.get(
                'https://data.gov.ua/api/3/action/package_show?id=7c51c4a0-104b-4540-a166-e9fc58485c1b').text
        except ConnectionError:
            logging.error('Error during general WantedPersons dataset JSON receiving occured')
        else:
            general_dataset_json = json.loads(general_dataset)
            logging.info('A general WantedPersons dataset JSON received')
        # get dataset id
        wanted_persons_general_dataset_id = general_dataset_json['result']['resources'][0]['id']
        try:
            # get resources JSON id
            wanted_persons_general_dataset_id_json = requests.get(
                'https://data.gov.ua/api/3/action/resource_show?id=' + wanted_persons_general_dataset_id).text
        except ConnectionError:
            logging.error('Error during WantedPersons resources JSON id receiving occured')
        else:
            wanted_persons_general_dataset_json = json.loads(wanted_persons_general_dataset_id_json)
            logging.info('A WantedPersons resources JSON id received')
        # get dataset json url
        wanted_persons_dataset_json_url = wanted_persons_general_dataset_json['result']['url']
        try:
            # get dataset
            wanted_persons_dataset_json = requests.get(wanted_persons_dataset_json_url).text
        except ConnectionError:
            logging.error('Error during WantedPersons dataset receiving occured')
        else:
            wanted_persons_dataset = json.loads(wanted_persons_dataset_json)
            logging.info('A WantedPersons dataset received')
        return wanted_persons_dataset

    @Dataset.measure_execution_time
    def __save_dataset(self, json):
        wanted_persons_col = self.db['WantedPersons']
        try:
            wanted_persons_col.insert_many(json)
        except PyMongoError:
            logging.error('Error during saving Wanted Persons Register into Database')
        else:
            logging.info('Wanted persons dataset was saved into the database')
        gc.collect()

    @Dataset.measure_execution_time
    def __clear_collection(self):
        if self.is_collection_exists('WantedPersons'):
            wanted_persons_col = self.db['WantedPersons']
            count_deleted_documents = wanted_persons_col.delete_many({})
            logging.warning(f'{count_deleted_documents.deleted_count} documents deleted. The wanted persons '
                            f'collection is empty.')

    @Dataset.measure_execution_time
    def __create_service_json(self):
        created_date = datetime.now()
        last_modified_date = datetime.now()
        wanted_persons_col = self.db['WantedPersons']
        documents_count = wanted_persons_col.count_documents({})
        wanted_persons_register_service_json = {
            '_id': 2,
            'Description': 'Інформація про осіб, які переховуються від органів влади',
            'DocumentsCount': documents_count,
            'CreatedDate': str(created_date),
            'LastModifiedDate': str(last_modified_date)
        }
        self.service_col.insert_one(wanted_persons_register_service_json)

    @Dataset.measure_execution_time
    def __update_service_json(self):
        last_modified_date = datetime.now()
        wanted_persons_col = self.db['WantedPersons']
        documents_count = wanted_persons_col.count_documents({})
        self.service_col.update_one(
            {'_id': 2},
            {'$set': {'LastModifiedDate': str(last_modified_date),
                      'DocumentsCount': documents_count}}
        )

    @Dataset.measure_execution_time
    def __update_metadata(self):
        # update or create WantedPersonsRegisterServiceJson
        if (self.is_collection_exists('ServiceCollection')) and (
                self.service_col.count_documents({'_id': 2}, limit=1) != 0):
            self.__update_service_json()
            logging.info('WantedPersonsRegisterServiceJson updated')
        else:
            self.__create_service_json()
            logging.info('WantedPersonsRegisterServiceJson created')

    @Dataset.measure_execution_time
    def __delete_collection_index(self):
        if self.is_collection_exists('WantedPersons'):
            wanted_persons_col = self.db['WantedPersons']
            if 'full_text' in wanted_persons_col.index_information():
                wanted_persons_col.drop_index('full_text')
                logging.warning('WantedPersons Text index deleted')

    @Dataset.measure_execution_time
    def __create_collection_index(self):
        wanted_persons_col = self.db['WantedPersons']
        wanted_persons_col.create_index(
            [('FIRST_NAME_U', 'text'), ('LAST_NAME_U', 'text'), ('MIDDLE_NAME_U', 'text')], name='full_text')
        logging.info('WantedPersons Text Index created')

    @Dataset.measure_execution_time
    def search_into_collection(self, query_string):
        wanted_persons_col = self.db['WantedPersons']
        final_result = 0
        try:
            result_count = wanted_persons_col.count_documents({'$text': {'$search': query_string}})
        except PyMongoError:
            logging.error('Error during search into Wanted Persons Register')
        else:
            if result_count == 0:
                logging.warning('The wanted persons register: No data found')
                final_result = 0
            else:
                logging.warning(f'The wanted persons register: {result_count} records found')
                final_result = wanted_persons_col.find({'$text': {'$search': query_string}},
                                                       {'score': {'$meta': 'textScore'}}) \
                    .sort([('score', {'$meta': 'textScore'})]).allow_disk_use(True)
        gc.collect()
        return final_result

    @Dataset.measure_execution_time
    def setup_dataset(self):
        self.__delete_collection_index()
        self.__clear_collection()
        __dataset = self.__get_dataset()
        self.__save_dataset(__dataset)
        self.__update_metadata()
        self.__create_collection_index()
