import gc
import json
import logging
import requests
from datetime import datetime
from pymongo.errors import PyMongoError


from .dataset import Dataset


class WantedPersonsRegister(Dataset):
    def __init__(self):
        super().__init__()

    @Dataset.measureExecutionTime
    def __getDataset(self):
        try:
            generalDataset = requests.get(
                'https://data.gov.ua/api/3/action/package_show?id=7c51c4a0-104b-4540-a166-e9fc58485c1b').text
        except:
            logging.error(
                'Error during general WantedPersons dataset JSON receiving occured')
        else:
            generalDatasetJson = json.loads(generalDataset)
            logging.info('A general WantedPersons dataset JSON received')
        # get dataset id
        wantedPersonsGeneralDatasetId = generalDatasetJson['result']['resources'][0]['id']
        try:
            # get resources JSON id
            wantedPersonsGeneralDatasetIdJson = requests.get(
                'https://data.gov.ua/api/3/action/resource_show?id=' + wantedPersonsGeneralDatasetId).text
        except:
            logging.error(
                'Error during WantedPersons resources JSON id receiving occured')
        else:
            wantedPersonsGeneralDatasetJson = json.loads(
                wantedPersonsGeneralDatasetIdJson)
            logging.info('A WantedPersons resources JSON id received')
        # get dataset json url
        wantedPersonsDatasetJsonUrl = wantedPersonsGeneralDatasetJson['result']['url']
        try:
            # get dataset
            wantedPersonsDatasetJson = requests.get(
                wantedPersonsDatasetJsonUrl).text
        except:
            logging.error(
                'Error during WantedPersons dataset receiving occured')
        else:
            wantedPersonsDataset = json.loads(wantedPersonsDatasetJson)
            logging.info('A WantedPersons dataset received')
        return wantedPersonsDataset

    @Dataset.measureExecutionTime
    def __saveDataset(self, json):
        wantedPersonsCol = self.db['WantedPersons']
        try:
            wantedPersonsCol.insert_many(json)
        except PyMongoError:
            logging.error(
                'Error during saving Wanted Persons Register into Database')
        else:
            logging.info('Wanted persons dataset was saved into the database')
        gc.collect()

    @Dataset.measureExecutionTime
    def __clearCollection(self):
        wantedPersonsCol = self.db['WantedPersons']
        countDeletedDocuments = wantedPersonsCol.delete_many({})
        logging.warning('%s documents deleted. The wanted persons collection is empty.', str(
            countDeletedDocuments.deleted_count))

    @Dataset.measureExecutionTime
    def __createServiceJson(self):
        createdDate = datetime.now()
        lastModifiedDate = datetime.now()
        wantedPersonsCol = self.db['WantedPersons']
        documentsCount = wantedPersonsCol.count_documents({})
        wantedPersonsRegisterServiceJson = {
            '_id': 2,
            'Description': 'Інформація про осіб, які переховуються від органів влади',
            'DocumentsCount': documentsCount,
            'CreatedDate': str(createdDate),
            'LastModifiedDate': str(lastModifiedDate)
        }
        self.serviceCol.insert_one(wantedPersonsRegisterServiceJson)

    @Dataset.measureExecutionTime
    def __updateServiceJson(self):
        lastModifiedDate = datetime.now()
        wantedPersonsCol = self.db['WantedPersons']
        documentsCount = wantedPersonsCol.count_documents({})
        self.serviceCol.update_one(
            {'_id': 2},
            {'$set': {'LastModifiedDate': str(lastModifiedDate),
                      'DocumentsCount': documentsCount}}
        )

    @Dataset.measureExecutionTime
    def __updateMetadata(self):
        collectionsList = self.db.list_collection_names()
        # update or create WantedgPersonsRegisterServiceJson
        if ('ServiceCollection' in collectionsList) and (self.serviceCol.count_documents({'_id': 2}, limit=1) != 0):
            self.__updateServiceJson()
            logging.info('WantedPersonsRegisterServiceJson updated')
        else:
            self.__createServiceJson()
            logging.info('WantedPersonsRegisterServiceJson created')

    @Dataset.measureExecutionTime
    def __deleteCollectionIndex(self):
        wantedPersonsCol = self.db['WantedPersons']
        if ('full_text' in wantedPersonsCol.index_information()):
            wantedPersonsCol.drop_index('full_text')
            logging.warning('WantedPersons Text index deleted')

    @Dataset.measureExecutionTime
    def __createCollectionIndex(self):
        wantedPersonsCol = self.db['WantedPersons']
        wantedPersonsCol.create_index(
            [('FIRST_NAME_U', 'text'), ('LAST_NAME_U', 'text'), ('MIDDLE_NAME_U', 'text')], name='full_text')
        logging.info('WantedPersons Text Index created')

    @Dataset.measureExecutionTime
    def searchIntoCollection(self, queryString):
        wantedPersonsCol = self.db['WantedPersons']
        finalResult = 0
        try:
            resultCount = wantedPersonsCol.count_documents(
                {'$text': {'$search': queryString}})
        except PyMongoError:
            logging.error(
                'Error during search into Wanted Persons Register')
        else:
            if resultCount == 0:
                logging.warning('The wanted persons register: No data found')
                finalResult = 0
            else:
                logging.warning(
                    'The wanted persons register: %s records found', str(resultCount))
                finalResult = wantedPersonsCol.find({'$text': {'$search': queryString}}, {
                                                    'score': {'$meta': 'textScore'}}).sort([('score', {'$meta': 'textScore'})])
        gc.collect()
        return finalResult

    @Dataset.measureExecutionTime
    def setupDataset(self):
        self.__deleteCollectionIndex()
        self.__clearCollection()
        __dataset = self.__getDataset()
        self.__saveDataset(__dataset)
        self.__updateMetadata()
        self.__createCollectionIndex()
