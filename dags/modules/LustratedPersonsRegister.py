#  Copyright (c) 2023 Andrii Malchyk, All rights reserved.

import gc
import json
import logging
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime
from io import BytesIO

import requests
from pymongo.errors import PyMongoError

from .dataset import Dataset, measure_execution_time


class LustratedPersonsRegister(Dataset):
    def __init__(self, connection_string, package_base_url, resource_base_url, package_resource_id):
        super().__init__(connection_string, package_base_url, resource_base_url, package_resource_id)

    @measure_execution_time
    def setup_dataset(self):
        self.__delete_collection_index()
        self.__clear_collection()
        __lustrated_dataset_zip_url = self.__get_dataset()
        self.__save_dataset(__lustrated_dataset_zip_url)
        self.__update_metadata()
        self.__create_collection_index()

    @measure_execution_time
    def __delete_collection_index(self):
        if self.is_collection_exists('Lustrated'):
            lustrated_col = self.db['Lustrated']
            if 'full_text' in lustrated_col.index_information():
                lustrated_col.drop_index('full_text')
                logging.warning('Lustrated Text index deleted')

    @measure_execution_time
    def __clear_collection(self):
        if self.is_collection_exists('Lustrated'):
            lustrated_col = self.db['Lustrated']
            count_deleted_documents = lustrated_col.delete_many({})
            logging.warning(f'{count_deleted_documents.deleted_count} documents deleted. The Lustrated Persons '
                            f'collection is empty.')

    @measure_execution_time
    def __get_dataset(self):
        try:
            general_dataset = requests.get(self.package_base_url + self.package_resource_id).text
        except ConnectionError as e:
            logging.error(f'Error during general LustratedPersonsRegister dataset JSON receiving occurred: {e}')
        else:
            general_dataset_json = json.loads(general_dataset)
            logging.info('A general LustratedPersonsRegister dataset JSON received')
        # get dataset id
        lustrated_persons_general_dataset_id = general_dataset_json['result']['resources'][0]['id']
        try:
            # get resources JSON id
            lustrated_persons_general_dataset_id_json = requests.get(
                    self.resource_base_url + lustrated_persons_general_dataset_id).text
        except ConnectionError as e:
            logging.error(f'Error during LustratedPersonsRegister resources JSON id receiving occurred: {e}')
        else:
            lustrated_persons_general_dataset_json = json.loads(lustrated_persons_general_dataset_id_json)
            logging.info('A LustratedPersonsRegister resources JSON id received')
        # get ZIP url
        lustrated_persons_dataset_zip_url = lustrated_persons_general_dataset_json['result']['url']
        return lustrated_persons_dataset_zip_url

    @measure_execution_time
    def __save_dataset(self, zip_url):
        lustrated_col = self.db['Lustrated']
        try:
            # get ZIP file
            lustrated_dataset_zip = requests.get(zip_url).content
        except OSError as e:
            logging.error(f'Error during LustratedPersonsRegister ZIP receiving occurred: {e}')
        else:
            logging.info('A LustratedPersonsRegister dataset received')
            lustrated_list = []
            with zipfile.ZipFile(BytesIO(lustrated_dataset_zip), 'r') as zip:
                for xml_file in zip.namelist():
                    logging.warning(f'File in ZIP: {xml_file}')
                    with zip.open(xml_file) as f:
                        # parse xml
                        tree = ET.parse(f)
                        xml_data = tree.getroot()
                        for record in xml_data:
                            fio = record.find('FIO').text
                            job = record.find('JOB').text
                            judgment_composition = record.find('JUDGMENT_COMPOSITION').text
                            period = record.find('PERIOD').text
                            lustrated_json = {
                                    'fio': fio,
                                    'job': job,
                                    'judgment_composition': judgment_composition,
                                    'period': period
                            }
                            lustrated_list.append(lustrated_json)
            try:
                # save to the collection
                lustrated_col.insert_many(lustrated_list, ordered=False)
            except PyMongoError as e:
                logging.error(f'Error during saving into Database: {e}')
            logging.info('Lustrated Persons dataset was saved into the database')
        gc.collect()

    @measure_execution_time
    def __update_metadata(self):
        # update or create LustratedPersonsRegisterServiceJson
        if (self.is_collection_exists('ServiceCollection')) and (
                self.service_col.count_documents({'_id': 6}, limit=1) != 0):
            self.__update_service_json()
            logging.info('LustratedPersonsRegisterServiceJson updated')
        else:
            self.__create_service_json()
            logging.info('LustratedPersonsRegisterServiceJson created')

    @measure_execution_time
    def __update_service_json(self):
        last_modified_date = datetime.now()
        lustrated_col = self.db['Lustrated']
        documents_count = lustrated_col.count_documents({})
        self.service_col.update_one(
                {'_id': 6},
                {'$set': {'LastModifiedDate': str(last_modified_date),
                          'DocumentsCount': documents_count}}
        )

    @measure_execution_time
    def __create_service_json(self):
        created_date = datetime.now()
        last_modified_date = datetime.now()
        lustrated_col = self.db['Lustrated']
        documents_count = lustrated_col.count_documents({})
        lustrated_register_service_json = {
                '_id': 6,
                'Description': 'Єдиний державний реєстр осіб, щодо яких застосовано положення Закону України «Про очищення влади»',
                'DocumentsCount': documents_count,
                'CreatedDate': str(created_date),
                'LastModifiedDate': str(last_modified_date)
        }
        self.service_col.insert_one(lustrated_register_service_json)

    @measure_execution_time
    def __create_collection_index(self):
        lustrated_col = self.db['Lustrated']
        lustrated_col.create_index([('fio', 'text')], name='full_text')
        logging.info('Lustrated Text Index created')
