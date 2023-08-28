#  Copyright (c) 2023 Andrii Malchyk, All rights reserved.
from mongoengine import *


class MissingPerson(Document):
    mongo_id = ObjectIdField(db_field="_id")
    id = IntField(db_field="ID", required=True)
    ovd = StringField(db_field="OVD", max_length=400, required=True)
    category = StringField(db_field="CATEGORY", max_length=400, required=True)
    first_name_u = StringField(db_field="FIRST_NAME_U", max_length=400, required=True)
    last_name_u = StringField(db_field="LAST_NAME_U", max_length=400, required=True)
    middle_name_u = StringField(db_field="MIDDLE_NAME_U", max_length=400, required=True)
    first_name_r = StringField(db_field="FIRST_NAME_R", max_length=400, required=True)
    last_name_r = StringField(db_field="LAST_NAME_R", max_length=400, required=True)
    middle_name_r = StringField(db_field="MIDDLE_NAME_R", max_length=400, required=True)
    first_name_e = StringField(db_field="FIRST_NAME_E", max_length=400, required=False)
    last_name_e = StringField(db_field="LAST_NAME_E", max_length=400, required=False)
    middle_name_e = StringField(db_field="MIDDLE_NAME_E", max_length=400, required=False)
    birth_date = DateTimeField(db_field="BIRTH_DATE", required=True)
    sex = StringField(db_field="SEX", max_length=400, required=True)
    lost_date = DateTimeField(db_field="LOST_DATE", required=True)
    lost_place = StringField(db_field="LOST_PLACE", max_length=400, required=True)
    article_crime = StringField(db_field="ARTICLE_CRIM", max_length=400, required=True)
    restraint = StringField(db_field="RESTRAINT", max_length=400, required=False)
    contact = StringField(db_field="CONTACT", max_length=400, required=True)
    photo_id = IntField(db_field="PHOTOID", required=False)
    meta = {'db_alias': 'searchmydata', 'collection': 'MissingPersons'}
