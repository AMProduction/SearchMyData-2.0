#  Copyright (c) 2023 Andrii Malchyk, All rights reserved.
import logging
import os
from datetime import datetime, timedelta

DOCUMENTS_PER_PAGE = int(os.getenv("DOCUMENTS_PER_PAGE"))


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

    expired_time = datetime.now() - timedelta(days=2)
    return any(
        datetime.strptime(record["last_modified_date"], "%Y-%m-%d %H:%M:%S.%f")
        < expired_time
        for record in RegisterInfo.objects
    )


def get_search_result_count(collection_name, query_string: str) -> int:
    """
    Return search result count.
    :param collection_name: where to search
    :param query_string: what to search
    :return: results count
    """
    try:
        result_count = collection_name.objects.search_text(query_string).count()
    except Exception as e:
        logging.error(f"Error during search into {collection_name} occurred: {e}")
    else:
        if result_count:
            logging.warning(f"{collection_name}: {result_count} records found")
            return result_count
        else:
            logging.warning(f"{collection_name}: No data found")
            return 0


def search_into_collection(collection_name, query_string: str, page_number: int = 0):
    """
    Search into a collection.
    :param collection_name: where to search
    :param query_string: what to search
    :param page_number: page to show
    :return: the search results
    """
    to_skip = page_number * DOCUMENTS_PER_PAGE
    return (
        collection_name.objects[to_skip : to_skip + DOCUMENTS_PER_PAGE]
        .search_text(query_string)
        .order_by("$text_score")
    )


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
