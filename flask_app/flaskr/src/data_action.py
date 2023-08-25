#  Copyright (c) 2023 Andrii Malchyk, All rights reserved.
import gc
import logging
from datetime import datetime, timedelta

from pymongo.errors import PyMongoError

DOCUMENTS_PER_PAGE = 100


def get_registers_info():
    """
    Show the list of available registers, count of documents, and the last update date
    :return: result set
    """
    from ..models.service_collection_model import RegisterInfo
    return RegisterInfo.objects.all()


def check_is_expired() -> bool:
    """
    Check if a dataset last updated date is older than 2 days ago.
    :return: if is expired
    """
    from ..models.service_collection_model import RegisterInfo
    is_expired = False
    expired_time = datetime.now() - timedelta(days=2)
    for record in RegisterInfo.objects:
        last_modified_date = datetime.strptime(record['last_modified_date'], '%Y-%m-%d %H:%M:%S.%f')
        if last_modified_date < expired_time:
            logging.warning(f'{record["description"]} is out of date')
            is_expired = True
    return is_expired


def search_into_collection(collection_name, query_string: str, page_number: int = 0):
    """
    Search into a collection.
    :param collection_name: page to show
    :param query_string: where to search
    :param page_number: what to search
    :return: the search results
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
    :param documents_count: amount of documents
    :return: count of pages
    """
    result = documents_count // DOCUMENTS_PER_PAGE
    if documents_count % DOCUMENTS_PER_PAGE:
        result += 1
    return result
