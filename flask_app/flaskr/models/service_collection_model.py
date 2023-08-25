#  Copyright (c) 2023 Andrii Malchyk, All rights reserved.
from mongoengine import *


class RegisterInfo(Document):
    id = IntField(db_field="_id", required=True, primary_key=True)
    description = StringField(db_field="Description", max_length=400, required=True)
    documents_count = IntField(db_field="DocumentsCount", required=True)
    created_date = DateTimeField(db_field="CreatedDate", required=True)
    last_modified_date = DateTimeField(db_field="LastModifiedDate", required=True)
    meta = {'db_alias': 'searchmydata',
            'collection': 'ServiceCollection'}
