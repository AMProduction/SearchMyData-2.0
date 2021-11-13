import gc
import logging
from datetime import datetime
from pymongo.errors import PyMongoError


from .dataset import Dataset


class EntrepreneursRegister(Dataset):
    def __init__(self):
        super().__init__()

    @Dataset.measureExecutionTime
    def getDataset(self):
        logging.info('EntrepreneursRegister getDataset call')

    @Dataset.measureExecutionTime
    def saveDataset(self):
        logging.info('EntrepreneursRegister saveDataset call')

    @Dataset.measureExecutionTime
    def clearCollection(self):
        entrepreneursCol = self.db['Entrepreneurs']
        countDeletedDocuments = entrepreneursCol.delete_many({})
        logging.warning('%s documents deleted. The entrepreneurs collection is empty.', str(
            countDeletedDocuments.deleted_count))

    @Dataset.measureExecutionTime
    def __createServiceJson(self):
        createdDate = datetime.now()
        lastModifiedDate = datetime.now()
        entrepreneursCol = self.db['Entrepreneurs']
        documentsCount = entrepreneursCol.count_documents({})
        entrepreneursRegisterServiceJson = {
            '_id': 5,
            'Description': 'Єдиний державний реєстр фізичних осіб – підприємців',
            'DocumentsCount': documentsCount,
            'CreatedDate': str(createdDate),
            'LastModifiedDate': str(lastModifiedDate)
        }
        self.serviceCol.insert_one(entrepreneursRegisterServiceJson)

    @Dataset.measureExecutionTime
    def __updateServiceJson(self):
        lastModifiedDate = datetime.now()
        entrepreneursCol = self.db['Entrepreneurs']
        documentsCount = entrepreneursCol.count_documents({})
        self.serviceCol.update_one(
            {'_id': 5},
            {'$set': {'LastModifiedDate': str(lastModifiedDate),
                      'DocumentsCount': documentsCount}}
        )

    @Dataset.measureExecutionTime
    def updateMetadata(self):
        collectionsList = self.db.list_collection_names()
        # update or create EntrepreneursRegisterServiceJson
        if ('ServiceCollection' in collectionsList) and (self.serviceCol.count_documents({'_id': 5}, limit=1) != 0):
            self.__updateServiceJson()
            logging.info('EntrepreneursRegisterServiceJson updated')
        else:
            self.__createServiceJson()
            logging.info('EntrepreneursRegisterServiceJson created')

    @Dataset.measureExecutionTime
    def deleteCollectionIndex(self):
        entrepreneursCol = self.db['Entrepreneurs']
        if ('full_text' in entrepreneursCol.index_information()):
            entrepreneursCol.drop_index('full_text')
            logging.warning('Entrepreneurs Text index deleted')

    @Dataset.measureExecutionTime
    def createCollectionIndex(self):
        entrepreneursCol = self.db['Entrepreneurs']
        entrepreneursCol.create_index([('fio', 'text')], name='full_text')
        logging.info('Entrepreneurs Text Index created')

    @Dataset.measureExecutionTime
    def searchIntoCollection(self, queryString):
        entrepreneursCol = self.db['Entrepreneurs']
        finalResult = 0
        try:
            resultCount = entrepreneursCol.count_documents(
                {'$text': {'$search': queryString}})
        except PyMongoError:
            logging.error(
                'Error during search into Entrepreneurs Register')
        else:
            if resultCount == 0:
                logging.warning('The Entrepreneurs register: No data found')
                finalResult = 0
            else:
                logging.warning(
                    'The Entrepreneurs register: %s records found', str(resultCount))
                finalResult = entrepreneursCol.find({'$text': {'$search': queryString}}, {'score': {
                                                    '$meta': 'textScore'}}).sort([('score', {'$meta': 'textScore'})]).allow_disk_use(True)
        gc.collect()
        return finalResult
