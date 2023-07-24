#  Copyright (c) 2023 Andrii Malchyk, All rights reserved.

import csv
import gc
import json
import logging
import os
import zipfile
from datetime import datetime
from io import BytesIO

import requests
from pymongo.errors import PyMongoError

from .dataset import Dataset


class DebtorsRegister(Dataset):
    def __init__(self, connection_string):
        super().__init__(connection_string)

    @Dataset.measure_execution_time
    def __get_dataset(self):
        try:
            general_dataset = requests.get(
                    'https://data.gov.ua/api/3/action/package_show?id=506734bf-2480-448c-a2b4-90b6d06df11e').text
        except ConnectionError:
            logging.error('Error during general DebtorsRegister dataset JSON receiving occured')
        else:
            general_dataset_json = json.loads(general_dataset)
            logging.info('A general DebtorsRegister dataset JSON received')
        # get dataset id
        debtors_general_dataset_id = general_dataset_json['result']['resources'][0]['id']
        try:
            # get resources JSON id
            debtors_general_dataset_id_json = requests.get(
                    'https://data.gov.ua/api/3/action/resource_show?id=' + debtors_general_dataset_id).text
        except ConnectionError:
            logging.error('Error during DebtorsRegister resources JSON id receiving occured')
        else:
            debtors_general_dataset_json = json.loads(debtors_general_dataset_id_json)
            logging.info('A DebtorsRegister resources JSON id received')
        # get ZIP url
        debtors_dataset_zip_url = debtors_general_dataset_json['result']['url']
        return debtors_dataset_zip_url

    @Dataset.measure_execution_time
    def __save_dataset(self, zip_url):
        debtors_col = self.db['Debtors']
        try:
            # get ZIP file
            debtors_dataset_zip = requests.get(zip_url).content
        except OSError:
            logging.error('Error during DebtorsRegisterZIP receiving occured')
        else:
            logging.info('A DebtorsRegister dataset received')
            # get lists of file
            debtors_zip = zipfile.ZipFile(BytesIO(debtors_dataset_zip), 'r')
            # go inside ZIP
            for csvFile in debtors_zip.namelist():
                logging.warning('File in ZIP: ' + str(csvFile))
                debtors_csv_file_name = str(csvFile)
            debtors_zip.extractall()
            debtors_zip.close()
            # get the columns names
            with open(debtors_csv_file_name, "r", encoding='windows-1251') as csvfile:
                columns_reader = csv.reader(csvfile)
                for row in columns_reader:
                    columns = row[0].split(";")
                    break
            with open(debtors_csv_file_name, "r", encoding='windows-1251') as csvfile:
                datareader = csv.DictReader(csvfile, fieldnames=columns)
                # skip the header
                next(datareader)
                for row in datareader:
                    try:
                        # save to the collection
                        debtors_col.insert_one(row)
                    except PyMongoError:
                        logging.error('Error during saving Debtors Register into Database')
            logging.info('Debtors dataset was saved into the database')
        finally:
            # delete temp files
            os.remove(debtors_csv_file_name)
        gc.collect()

    @Dataset.measure_execution_time
    def __clear_collection(self):
        if self.is_collection_exists('Debtors'):
            debtors_col = self.db['Debtors']
            count_deleted_documents = debtors_col.delete_many({})
            logging.warning(f'{count_deleted_documents.deleted_count} documents deleted. The wanted persons '
                            f'collection is empty.')

    @Dataset.measure_execution_time
    def __create_service_json(self):
        created_date = datetime.now()
        last_modified_date = datetime.now()
        debtors_col = self.db['Debtors']
        documents_count = debtors_col.count_documents({})
        debtors_register_service_json = {
                '_id': 3,
                'Description': 'Єдиний реєстр боржників',
                'DocumentsCount': documents_count,
                'CreatedDate': str(created_date),
                'LastModifiedDate': str(last_modified_date)
        }
        self.service_col.insert_one(debtors_register_service_json)

    @Dataset.measure_execution_time
    def __update_service_json(self):
        last_modified_date = datetime.now()
        debtors_col = self.db['Debtors']
        documents_count = debtors_col.count_documents({})
        self.service_col.update_one(
                {'_id': 3},
                {'$set': {'LastModifiedDate': str(last_modified_date),
                          'DocumentsCount': documents_count}}
        )

    @Dataset.measure_execution_time
    def __update_metadata(self):
        # update or create DebtorsRegisterServiceJson
        if (self.is_collection_exists('ServiceCollection')) and (
                self.service_col.count_documents({'_id': 3}, limit=1) != 0):
            self.__update_service_json()
            logging.info('DebtorsRegisterServiceJson updated')
        else:
            self.__create_service_json()
            logging.info('DebtorsRegisterServiceJson created')

    @Dataset.measure_execution_time
    def __delete_collection_index(self):
        if self.is_collection_exists('Debtors'):
            debtors_col = self.db['Debtors']
            if 'full_text' in debtors_col.index_information():
                debtors_col.drop_index('full_text')
                logging.warning('Debtors Text index deleted')

    @Dataset.measure_execution_time
    def __create_collection_index(self):
        debtors_col = self.db['Debtors']
        debtors_col.create_index([('DEBTOR_NAME', 'text')], name='full_text')
        logging.info('Debtors Text Index created')

    @Dataset.measure_execution_time
    def search_into_collection(self, query_string):
        debtors_col = self.db['Debtors']
        final_result = 0
        try:
            result_count = debtors_col.count_documents({'$text': {'$search': query_string}})
        except PyMongoError:
            logging.error('Error during search into Debtors Register')
        else:
            if result_count == 0:
                logging.warning('The debtors register: No data found')
                final_result = 0
            else:
                logging.warning(f'The debtors register: {result_count} records found')
                final_result = debtors_col.find({'$text': {'$search': query_string}}, {'score': {'$meta': 'textScore'}}) \
                    .sort([('score', {'$meta': 'textScore'})]).allow_disk_use(True)
        gc.collect()
        return final_result

    @Dataset.measure_execution_time
    def setup_dataset(self):
        self.__delete_collection_index()
        self.__clear_collection()
        __debtors_dataset_zip_url = self.__get_dataset()
        self.__save_dataset(__debtors_dataset_zip_url)
        self.__update_metadata()
        self.__create_collection_index()
