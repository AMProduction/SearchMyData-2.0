#  Copyright (c) 2023 Andrii Malchyk, All rights reserved.

import csv
import gc
import json
import logging
import zipfile
from datetime import datetime
from io import BytesIO, TextIOWrapper

import requests
from pymongo.errors import PyMongoError

from .dataset import Dataset, measure_execution_time


class DebtorsRegister(Dataset):
    def __init__(self, connection_string, package_base_url, resource_base_url, package_resource_id):
        super().__init__(connection_string, package_base_url, resource_base_url, package_resource_id)

    @measure_execution_time
    def setup_dataset(self):
        self.__delete_collection_index()
        self.__clear_collection()
        __debtors_dataset_zip_url = self.__get_dataset()
        self.__save_dataset(__debtors_dataset_zip_url)
        self.__update_metadata()
        self.__create_collection_index()

    @measure_execution_time
    def __delete_collection_index(self):
        if self.is_collection_exists('Debtors'):
            debtors_col = self.db['Debtors']
            if 'full_text' in debtors_col.index_information():
                debtors_col.drop_index('full_text')
                logging.warning('Debtors Text index deleted')

    @measure_execution_time
    def __clear_collection(self):
        if self.is_collection_exists('Debtors'):
            debtors_col = self.db['Debtors']
            count_deleted_documents = debtors_col.delete_many({})
            logging.warning(f'{count_deleted_documents.deleted_count} documents deleted. The debtors '
                            f'collection is empty.')

    @measure_execution_time
    def __get_dataset(self):
        try:
            general_dataset = requests.get(self.package_base_url + self.package_resource_id).text
        except ConnectionError as e:
            logging.error(f'Error during general DebtorsRegister dataset JSON receiving occurred: {e}')
        else:
            general_dataset_json = json.loads(general_dataset)
            logging.info('A general DebtorsRegister dataset JSON received')
        # get dataset id
        debtors_general_dataset_id = general_dataset_json['result']['resources'][0]['id']
        try:
            # get resources JSON id
            debtors_general_dataset_id_json = requests.get(self.resource_base_url + debtors_general_dataset_id).text
        except ConnectionError as e:
            logging.error(f'Error during DebtorsRegister resources JSON id receiving occurred: {e}')
        else:
            debtors_general_dataset_json = json.loads(debtors_general_dataset_id_json)
            logging.info('A DebtorsRegister resources JSON id received')
        # get ZIP url
        debtors_dataset_zip_url = debtors_general_dataset_json['result']['url']
        return debtors_dataset_zip_url

    @measure_execution_time
    def __save_dataset(self, zip_url):
        debtors_col = self.db['Debtors']
        try:
            # get ZIP file
            debtors_dataset_zip = requests.get(zip_url).content
        except OSError as e:
            logging.error(f'Error during DebtorsRegisterZIP receiving occurred: {e}')
        else:
            logging.info('A DebtorsRegister dataset received')
            # get the columns names
            with zipfile.ZipFile(BytesIO(debtors_dataset_zip), 'r') as zip:
                for csv_file in zip.namelist():
                    logging.warning(f'File in ZIP: {csv_file}')
                    with zip.open(csv_file, "r") as csvfile:
                        columns_reader = csv.reader(TextIOWrapper(csvfile, newline='', encoding='windows-1251'))
                        for row in columns_reader:
                            columns = row[0].split(";")
                            break
            with zipfile.ZipFile(BytesIO(debtors_dataset_zip), 'r') as zip:
                for csv_file in zip.namelist():
                    with zip.open(csv_file, "r") as csvfile:
                        datareader = csv.DictReader(TextIOWrapper(csvfile, newline='', encoding='windows-1251'),
                                                    fieldnames=columns)
                        # skip the header
                        next(datareader)
                        for row in datareader:
                            try:
                                # save to the collection
                                debtors_col.insert_one(row)
                            except PyMongoError:
                                logging.error(f'Error during saving {row} into Database')
            logging.info('Debtors dataset was saved into the database')
        gc.collect()

    @measure_execution_time
    def __update_metadata(self):
        # update or create DebtorsRegisterServiceJson
        if (self.is_collection_exists('ServiceCollection')) and (
                self.service_col.count_documents({'_id': 3}, limit=1) != 0):
            self.__update_service_json()
            logging.info('DebtorsRegisterServiceJson updated')
        else:
            self.__create_service_json()
            logging.info('DebtorsRegisterServiceJson created')

    @measure_execution_time
    def __update_service_json(self):
        last_modified_date = datetime.now()
        debtors_col = self.db['Debtors']
        documents_count = debtors_col.count_documents({})
        self.service_col.update_one(
                {'_id': 3},
                {'$set': {'LastModifiedDate': str(last_modified_date),
                          'DocumentsCount': documents_count}}
        )

    @measure_execution_time
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

    @measure_execution_time
    def __create_collection_index(self):
        debtors_col = self.db['Debtors']
        debtors_col.create_index([('DEBTOR_NAME', 'text')], name='full_text')
        logging.info('Debtors Text Index created')
