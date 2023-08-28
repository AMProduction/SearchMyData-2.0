#  Copyright (c) 2023 Andrii Malchyk, All rights reserved.
from mongoengine import *


class LustratedPerson(Document):
    fio = StringField(db_field="fio", max_length=200, required=True)
    job = StringField(db_field="job", max_length=600, required=True)
    judgment_composition = StringField(db_field="judgment_composition", max_length=400, required=True)
    period = StringField(db_field="period", max_length=400, required=True)
    meta = {'db_alias': 'searchmydata', 'collection': 'Lustrated'}
