#  Copyright (c) 2023 Andrii Malchyk, All rights reserved.
import gc
import logging
from datetime import datetime, timedelta

from pymongo.errors import PyMongoError

DOCUMENTS_PER_PAGE = 100


def get_registers_info(service_collection_name):
    """Show the list of available registers, count of documents, and the last update date.
    @param service_collection_name: a service collection name
    @return: result set
    """
    result = service_collection_name.find({}, {'_id': 1, 'Description': 1, 'DocumentsCount': 1,
                                               'LastModifiedDate': 1}).sort([('_id', 1)])
    return result


def check_is_expired(service_collection_name) -> bool:
    """Check if a dataset last updated date is older than 2 days ago.
    @param service_collection_name: a service collection name
    @return: if is expired
    """
    is_expired = False
    expired_time = datetime.now() - timedelta(days=2)
    for record in service_collection_name.find():
        last_modified_date = datetime.strptime(record['LastModifiedDate'], '%Y-%m-%d %H:%M:%S.%f')
        if last_modified_date < expired_time:
            logging.warning(f'{record["Description"]} is out of date')
            is_expired = True
    return is_expired


def search_into_collection(collection_name, query_string: str, page_number: int = 0):
    """
    Search into a collection.
    @param page_number: page to show
    @param collection_name: where to search
    @param query_string: what to search
    @return: the search results
    """
    try:
        result_count = collection_name.count_documents({'$text': {'$search': query_string}})
    except PyMongoError as e:
        logging.error(f'Error during search into {collection_name} occurred: {e}')
    else:
        if result_count == 0:
            logging.warning(f'{collection_name}: No data found')
            return 0, 0
        else:
            to_skip = page_number * DOCUMENTS_PER_PAGE
            logging.warning(f'{collection_name}: {result_count} records found')
            return result_count, collection_name.find({'$text': {'$search': query_string}},
                                                      {'score': {'$meta': 'textScore'}}, skip=to_skip,
                                                      limit=DOCUMENTS_PER_PAGE).sort(
                    [('score', {'$meta': 'textScore'})]).allow_disk_use(True)
    gc.collect()


def get_pages_count(documents_count: int) -> int:
    """
    The return amount of pages needs to represent the amount of the documents
    @param documents_count: amount of documents
    @return: count of pages
    """
    result = documents_count // DOCUMENTS_PER_PAGE
    if documents_count % DOCUMENTS_PER_PAGE:
        result += 1
    return result
