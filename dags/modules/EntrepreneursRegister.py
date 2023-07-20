#  Copyright (c) 2023 Andrii Malchyk, All rights reserved.

import gc
import logging
from datetime import datetime

from pymongo.errors import PyMongoError

from .dataset import Dataset


class EntrepreneursRegister(Dataset):
    def __init__(self):
        super().__init__()

    @Dataset.measure_execution_time
    def get_dataset(self):
        logging.info('EntrepreneursRegister getDataset call')

    @Dataset.measure_execution_time
    def save_dataset(self):
        logging.info('EntrepreneursRegister saveDataset call')

    @Dataset.measure_execution_time
    def clear_collection(self):
        if self.is_collection_exists('Entrepreneurs'):
            entrepreneurs_col = self.db['Entrepreneurs']
            count_deleted_documents = entrepreneurs_col.delete_many({})
            logging.warning(f'{count_deleted_documents.deleted_count} documents deleted. The entrepreneurs collection '
                            f'is empty.')

    @Dataset.measure_execution_time
    def __create_service_json(self):
        created_date = datetime.now()
        last_modified_date = datetime.now()
        entrepreneurs_col = self.db['Entrepreneurs']
        documents_count = entrepreneurs_col.count_documents({})
        entrepreneurs_register_service_json = {
            '_id': 5,
            'Description': 'Єдиний державний реєстр фізичних осіб – підприємців',
            'DocumentsCount': documents_count,
            'CreatedDate': str(created_date),
            'LastModifiedDate': str(last_modified_date)
        }
        self.service_col.insert_one(entrepreneurs_register_service_json)

    @Dataset.measure_execution_time
    def __update_service_json(self):
        last_modified_date = datetime.now()
        entrepreneurs_col = self.db['Entrepreneurs']
        documents_count = entrepreneurs_col.count_documents({})
        self.service_col.update_one(
            {'_id': 5},
            {'$set': {'LastModifiedDate': str(last_modified_date),
                      'DocumentsCount': documents_count}}
        )

    @Dataset.measure_execution_time
    def update_metadata(self):
        # update or create EntrepreneursRegisterServiceJson
        if (self.is_collection_exists('ServiceCollection')) and (
                self.service_col.count_documents({'_id': 5}, limit=1) != 0):
            self.__update_service_json()
            logging.info('EntrepreneursRegisterServiceJson updated')
        else:
            self.__create_service_json()
            logging.info('EntrepreneursRegisterServiceJson created')

    @Dataset.measure_execution_time
    def delete_collection_index(self):
        if self.is_collection_exists('Entrepreneurs'):
            entrepreneurs_col = self.db['Entrepreneurs']
            if 'full_text' in entrepreneurs_col.index_information():
                entrepreneurs_col.drop_index('full_text')
                logging.warning('Entrepreneurs Text index deleted')

    @Dataset.measure_execution_time
    def create_collection_index(self):
        entrepreneurs_col = self.db['Entrepreneurs']
        entrepreneurs_col.create_index([('fio', 'text')], name='full_text')
        logging.info('Entrepreneurs Text Index created')

    @Dataset.measure_execution_time
    def search_into_collection(self, query_string):
        entrepreneurs_col = self.db['Entrepreneurs']
        final_result = 0
        try:
            result_count = entrepreneurs_col.count_documents({'$text': {'$search': query_string}})
        except PyMongoError:
            logging.error('Error during search into Entrepreneurs Register')
        else:
            if result_count == 0:
                logging.warning('The Entrepreneurs register: No data found')
                final_result = 0
            else:
                logging.warning(f'The Entrepreneurs register: {result_count} records found')
                final_result = entrepreneurs_col.find({'$text': {'$search': query_string}},
                                                      {'score': {'$meta': 'textScore'}}) \
                    .sort([('score', {'$meta': 'textScore'})]).allow_disk_use(True)
        gc.collect()
        return final_result
