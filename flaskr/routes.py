#  Copyright (c) 2023 Andrii Malchyk, All rights reserved.
import os
from datetime import datetime, timedelta

from flask import render_template, request

from flaskr import app, mongo


@app.route("/")
@app.route("/index")
@app.route("/home")
def home():
    return render_template('home.html', status=True, index=True, now=datetime.utcnow())


@app.route('/info')
def get_collections_info():
    db = mongo[os.getenv('MONGO_INITDB_DATABASE')]
    service_collection = db['ServiceCollection']
    registers_info = service_collection.find({},
                                             {'_id': 1, 'Description': 1, 'DocumentsCount': 1, 'LastModifiedDate': 1}) \
        .sort([('_id', 1)])
    expiration = False
    expired_time = datetime.now() - timedelta(days=2)
    for record in service_collection.find():
        last_modified_date = datetime.strptime(record['LastModifiedDate'], '%Y-%m-%d %H:%M:%S.%f')
        if last_modified_date < expired_time:
            expiration = True
    return render_template('info.html', result=registers_info, isExpired=expiration, now=datetime.utcnow())


@app.route('/result', methods=['POST', 'GET'])
def get_search_results():
    from .src.DebtorsRegister import DebtorsRegister
    from .src.EntrepreneursRegister import EntrepreneursRegister
    from .src.LegalEntitiesRegister import LegalEntitiesRegister
    from .src.MissingPersonsRegister import MissingPersonsRegister
    from .src.WantedPersonsRegister import WantedPersonsRegister
    from .src.LustratedPersonsRegister import LustratedPersonsRegister
    # create instances
    missing_persons = MissingPersonsRegister()
    wanted_persons = WantedPersonsRegister()
    debtors = DebtorsRegister()
    legal_entities = LegalEntitiesRegister()
    entrepreneurs = EntrepreneursRegister()
    lustrated = LustratedPersonsRegister()
    if request.method == 'POST':
        search_string = request.form['search']
        # call search methods
        result_missing_persons = missing_persons.search_into_collection(search_string)
        result_wanted_persons = wanted_persons.search_into_collection(search_string)
        result_debtors = debtors.search_into_collection(search_string)
        result_legal_entities = legal_entities.search_into_collection(search_string)
        result_entrepreneurs = entrepreneurs.search_into_collection(search_string)
        result_lustrated = lustrated.search_into_collection(search_string)
        return render_template('result.html', now=datetime.utcnow(), resultMissingPersons=result_missing_persons,
                               resultWantedPersons=result_wanted_persons, resultDebtors=result_debtors,
                               resultLegalEntities=result_legal_entities, resultEntrepreneurs=result_entrepreneurs,
                               resultLustrated=result_lustrated)
