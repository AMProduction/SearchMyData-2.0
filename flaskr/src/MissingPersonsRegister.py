import gc
import json
import logging
import requests
from datetime import datetime
from pymongo.errors import PyMongoError


from .dataset import Dataset


class MissingPersonsRegister(Dataset):
    def __init__(self):
        super().__init__()

    @Dataset.measureExecutionTime
    def __getDataset(self):
        try:
            generalDataset = requests.get(
                'https://data.gov.ua/api/3/action/package_show?id=470196d3-4e7a-46b0-8c0c-883b74ac65f0').text
        except:
            logging.error(
                'Error during general MissingPersons dataset JSON receiving occured')
        else:
            generalDatasetJson = json.loads(generalDataset)
            logging.info('A general MissingPersons dataset JSON received')
        # get dataset id
        missingPersonsGeneralDatasetId = generalDatasetJson['result']['resources'][0]['id']
        try:
            # get resources JSON id
            missingPersonsGeneralDatasetIdJson = requests.get(
                'https://data.gov.ua/api/3/action/resource_show?id=' + missingPersonsGeneralDatasetId).text
        except:
            logging.error(
                'Error during MissingPersons resources JSON id receiving occured')
        else:
            missingPersonsGeneralDatasetJson = json.loads(
                missingPersonsGeneralDatasetIdJson)
            logging.info('A MissingPersons resources JSON id received')
        # get dataset json url
        missingPersonsDatasetJsonUrl = missingPersonsGeneralDatasetJson['result']['url']
        try:
            # get dataset
            missingPersonsDatasetJson = requests.get(
                missingPersonsDatasetJsonUrl).text
        except:
            logging.error(
                'Error during MissingPersons dataset receiving occured')
        else:
            missingPersonsDataset = json.loads(missingPersonsDatasetJson)
            logging.info('A MissingPersons dataset received')
        return missingPersonsDataset

    @Dataset.measureExecutionTime
    def __saveDataset(self, json):
        missingPersonsCol = self.db['MissingPersons']
        try:
            missingPersonsCol.insert_many(json)
        except PyMongoError:
            logging.error(
                'Error during saving Missing Persons Register into Database')
        else:
            logging.info('Missing persons dataset was saved into the database')
        gc.collect()

    @Dataset.measureExecutionTime
    def __clearCollection(self):
        missingPersonsCol = self.db['MissingPersons']
        countDeletedDocuments = missingPersonsCol.delete_many({})
        logging.warning('%s documents deleted. The missing persons collection is empty.', str(
            countDeletedDocuments.deleted_count))

    @Dataset.measureExecutionTime
    def __createServiceJson(self):
        createdDate = datetime.now()
        lastModifiedDate = datetime.now()
        missingPersonsCol = self.db['MissingPersons']
        documentsCount = missingPersonsCol.count_documents({})
        missingPersonsRegisterServiceJson = {
            '_id': 1,
            'Description': 'Інформація про безвісно зниклих громадян',
            'DocumentsCount': documentsCount,
            'CreatedDate': str(createdDate),
            'LastModifiedDate': str(lastModifiedDate)
        }
        self.serviceCol.insert_one(missingPersonsRegisterServiceJson)

    @Dataset.measureExecutionTime
    def __updateServiceJson(self):
        lastModifiedDate = datetime.now()
        missingPersonsCol = self.db['MissingPersons']
        documentsCount = missingPersonsCol.count_documents({})
        self.serviceCol.update_one(
            {'_id': 1},
            {'$set': {'LastModifiedDate': str(lastModifiedDate),
                      'DocumentsCount': documentsCount}}
        )

    @Dataset.measureExecutionTime
    def __updateMetadata(self):
        collectionsList = self.db.list_collection_names()
        # update or create MissingPersonsRegisterServiceJson
        if ('ServiceCollection' in collectionsList) and (self.serviceCol.count_documents({'_id': 1}, limit=1) != 0):
            self.__updateServiceJson()
            logging.info('MissingPersonsRegisterServiceJson updated')
        else:
            self.__createServiceJson()
            logging.info('MissingPersonsRegisterServiceJson created')

    @Dataset.measureExecutionTime
    def __deleteCollectionIndex(self):
        missingPersonsCol = self.db['MissingPersons']
        if ('full_text' in missingPersonsCol.index_information()):
            missingPersonsCol.drop_index('full_text')
            logging.warning('Missing persons Text index deleted')

    @Dataset.measureExecutionTime
    def __createCollectionIndex(self):
        missingPersonsCol = self.db['MissingPersons']
        missingPersonsCol.create_index(
            [('FIRST_NAME_U', 'text'), ('LAST_NAME_U', 'text'), ('MIDDLE_NAME_U', 'text')], name='full_text')
        logging.info('Missing persons Text Index created')

    @Dataset.measureExecutionTime
    def searchIntoCollection(self, queryString):
        missingPersonsCol = self.db['MissingPersons']
        finalResult = 0
        try:
            resultCount = missingPersonsCol.count_documents(
                {'$text': {'$search': queryString}})
        except PyMongoError:
            logging.error(
                'Error during search into Missing Persons Register')
        else:
            if resultCount == 0:
                logging.warning('The missing persons register: No data found')
                finalResult = 0
            else:
                logging.warning(
                    'The missing persons register: %s records found', str(resultCount))
                finalResult = missingPersonsCol.find({'$text': {'$search': queryString}}, {
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
