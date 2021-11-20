import gc
import json
import logging
import os
import shutil
import xml.etree.ElementTree as ET
import zipfile
import requests
from datetime import datetime
from io import BytesIO
from pymongo.errors import PyMongoError


from .dataset import Dataset


class LegalEntitiesRegister(Dataset):
    def __init__(self):
        super().__init__()

    @Dataset.measure_execution_time
    def get_dataset(self):
        try:
            general_dataset = requests.get(
                'https://data.gov.ua/api/3/action/package_show?id=1c7f3815-3259-45e0-bdf1-64dca07ddc10').text
        except ConnectionError:
            logging.error('Error during general EntrepreneursRegister dataset JSON receiving occured')
        else:
            general_dataset_json = json.loads(general_dataset)
            logging.info('A general EntrepreneursRegister dataset JSON received')
        # get dataset id
        entrepreneurs_general_dataset_id = general_dataset_json['result']['resources'][0]['id']
        try:
            # get resources JSON id
            entrepreneurs_general_dataset_id_json = requests.get(
                'https://data.gov.ua/api/3/action/resource_show?id=' + entrepreneurs_general_dataset_id).text
        except ConnectionError:
            logging.error('Error during EntrepreneursRegister resources JSON id receiving occured')
        else:
            entrepreneurs_general_dataset_json = json.loads(entrepreneurs_general_dataset_id_json)
            logging.info('A EntrepreneursRegister resources JSON id received')
        # get ZIP url
        entrepreneurs_dataset_zip_url = entrepreneurs_general_dataset_json['result']['url']
        return entrepreneurs_dataset_zip_url

    @Dataset.measure_execution_time
    def save_dataset(self, zip_url):
        entrepreneurs_col = self.db['Entrepreneurs']
        legal_entities_col = self.db['LegalEntities']
        try:
            # get ZIP file
            entrepreneurs_dataset_zip = requests.get(zip_url).content
        except OSError:
            logging.error('Error during EntrepreneursRegister ZIP receiving occured')
        else:
            logging.info('A EntrepreneursRegister dataset received')
            # get lists of file
            entrepreneurs_zip = zipfile.ZipFile(BytesIO(entrepreneurs_dataset_zip), 'r')
            # go inside ZIP
            for xml_file in entrepreneurs_zip.namelist():
                # skip root folder
                if xml_file.endswith('/'):
                    root_folder_name = xml_file
                    continue
                logging.warning('File in ZIP: ' + str(xml_file))
            # unzip all files
            entrepreneurs_zip.extractall('Temp')
            for xml_file in os.listdir('Temp/'+root_folder_name):
                if xml_file.find('_UO_') != -1:
                    # read the legal Entities Xml file
                    path_to_file = 'Temp/' + root_folder_name + xml_file
                    # parse xml
                    legal_entities_json = {}
                    tree = ET.parse(path_to_file)
                    xml_data = tree.getroot()
                    for record in xml_data:
                        name = record.find('NAME').text
                        short_name = record.find('SHORT_NAME').text
                        edrpou = record.find('EDRPOU').text
                        address = record.find('ADDRESS').text
                        kved = record.find('KVED').text
                        boss = record.find('BOSS').text
                        beneficiaries_dict = {}
                        beneficiaryNumber = 1
                        for beneficiaries in record.iter('BENEFICIARIES'):
                            if beneficiaries.find('BENEFICIARY') is not None:
                                for beneficiary in beneficiaries.iter('BENEFICIARY'):
                                    beneficiary_to_dict = beneficiary.text
                                    key = 'beneficiary' + str(beneficiaryNumber)
                                    beneficiaries_dict[key] = beneficiary_to_dict
                                    beneficiaryNumber += 1
                        founders_dict = {}
                        founders_number = 1
                        for founders in record.iter('FOUNDERS'):
                            if founders.find('FOUNDER') is not None:
                                for founder in founders.iter('FOUNDER'):
                                    founder_to_dict = founder.text
                                    key = 'founder' + str(founders_number)
                                    founders_dict[key] = founder_to_dict
                                    founders_number += 1
                        stan = record.find('STAN').text
                        legal_entities_json = {
                            'name': name,
                            'short_name': short_name,
                            'edrpou': edrpou,
                            'address': address,
                            'kved': kved,
                            'boss': boss,
                            'beneficiaries': beneficiaries_dict,
                            'founders': founders_dict,
                            'stan': stan
                        }
                        try:
                            # save to the collection
                            legal_entities_col.insert_one(legal_entities_json)
                        except PyMongoError:
                            logging.error('Error during saving Legal Entities Register into Database')
                    logging.info('LegalEntities dataset was saved into the database')
                if xml_file.find('_FOP_') != -1:
                    # read the entrepreneurs Xml file
                    path_to_file = 'Temp/' + root_folder_name + xml_file
                    # parse xml
                    entrepreneurs_json = {}
                    tree = ET.parse(path_to_file)
                    xml_data = tree.getroot()
                    for record in xml_data:
                        fio = record.find('FIO').text
                        address = record.find('ADDRESS').text
                        kved = record.find('KVED').text
                        stan = record.find('STAN').text
                        entrepreneurs_json = {
                            'fio': fio,
                            'address': address,
                            'kved': kved,
                            'stan': stan
                        }
                        try:
                            # save to the collection
                            entrepreneurs_col.insert_one(entrepreneurs_json)
                        except PyMongoError:
                            logging.error('Error during saving Entrepreneurs Register into Database')
                    logging.info('Entrepreneurs dataset was saved into the database')
        finally:
            # delete temp files
            shutil.rmtree('Temp', ignore_errors=True)
        gc.collect()

    @Dataset.measure_execution_time
    def clear_collection(self):
        legal_entities_col = self.db['LegalEntities']
        count_deleted_documents = legal_entities_col.delete_many({})
        logging.warning('%s documents deleted. The legal entities collection is empty.', str(
            count_deleted_documents.deleted_count))

    @Dataset.measure_execution_time
    def __create_service_json(self):
        created_date = datetime.now()
        last_modified_date = datetime.now()
        legal_entities_col = self.db['LegalEntities']
        documents_count = legal_entities_col.count_documents({})
        legal_entities_register_service_json = {
            '_id': 4,
            'Description': 'Єдиний державний реєстр юридичних осіб та громадських формувань',
            'DocumentsCount': documents_count,
            'CreatedDate': str(created_date),
            'LastModifiedDate': str(last_modified_date)
        }
        self.service_col.insert_one(legal_entities_register_service_json)

    @Dataset.measure_execution_time
    def __update_service_json(self):
        last_modified_date = datetime.now()
        legal_entities_col = self.db['LegalEntities']
        documents_count = legal_entities_col.count_documents({})
        self.service_col.update_one(
            {'_id': 4},
            {'$set': {'LastModifiedDate': str(last_modified_date),
                      'DocumentsCount': documents_count}}
        )

    @Dataset.measure_execution_time
    def update_metadata(self):
        collections_list = self.db.list_collection_names()
        # update or create LegalEntitiesRegisterServiceJson
        if ('ServiceCollection' in collections_list) and (self.service_col.count_documents({'_id': 4}, limit=1) != 0):
            self.__update_service_json()
            logging.info('LegalEntitiesRegisterServiceJson updated')
        else:
            self.__create_service_json()
            logging.info('LegalEntitiesRegisterServiceJson created')

    @Dataset.measure_execution_time
    def delete_collection_index(self):
        legal_entities_col = self.db['LegalEntities']
        if 'full_text' in legal_entities_col.index_information():
            legal_entities_col.drop_index('full_text')
            logging.warning('LegalEntities Text index deleted')

    @Dataset.measure_execution_time
    def create_collection_index(self):
        legal_entities_col = self.db['LegalEntities']
        legal_entities_col.create_index([('short_name', 'text'), ('edrpou', 'text'), ('boss', 'text'),
                                         ('beneficiaries', 'text'), ('founders', 'text')], name='full_text')
        logging.info('LegalEntities Text Index created')

    @Dataset.measure_execution_time
    def search_into_collection(self, query_string):
        legal_entities_col = self.db['LegalEntities']
        final_result = 0
        try:
            result_count = legal_entities_col.count_documents({'$text': {'$search': query_string}})
        except PyMongoError:
            logging.error('Error during search into Legal Entities Register')
        else:
            if result_count == 0:
                logging.warning('The legal entities register: No data found')
                final_result = 0
            else:
                logging.warning('The legal entities register: %s records found', str(result_count))
                final_result = legal_entities_col.find({'$text': {'$search': query_string}},
                                                       {'score': {'$meta': 'textScore'}})\
                    .sort([('score', {'$meta': 'textScore'})]).allow_disk_use(True)
        gc.collect()
        return final_result
