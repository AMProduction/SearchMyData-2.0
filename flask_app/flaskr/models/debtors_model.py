#  Copyright (c) 2023 Andrii Malchyk, All rights reserved.
from mongoengine import *


class Debtor(Document):
    mongo_id = ObjectIdField(db_field="_id")
    debtor_name = StringField(db_field="DEBTOR_NAME", max_length=200, required=True)
    debtor_birthdate = DateTimeField(db_field="DEBTOR_BIRTHDATE", required=False)
    debtor_code = IntField(db_field="DEBTOR_CODE", required=True)
    publisher = StringField(db_field="PUBLISHER", max_length=300, required=True)
    org_name = StringField(db_field="ORG_NAME", max_length=300, required=True)
    org_phone_num = StringField(db_field="ORG_PHONE_NUM", max_length=100, required=False)
    emp_full_fio = StringField(db_field="EMP_FULL_FIO", max_length=200, required=True)
    emp_phone_num = StringField(db_field="EMP_PHONE_NUM", max_length=400, required=False)
    email_addr = StringField(db_field="EMAIL_ADDR", max_length=400, required=False)
    vp_ordernum = IntField(db_field="VP_ORDERNUM", required=True)
    vd_cat = StringField(db_field="VD_CAT", max_length=400, required=True)
    meta = {'db_alias': 'searchmydata', 'collection': 'Debtors'}
