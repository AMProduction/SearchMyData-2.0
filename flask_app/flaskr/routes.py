#  Copyright (c) 2023 Andrii Malchyk, All rights reserved.
import os
from datetime import datetime

from flask import render_template

from flaskr import app, mongo
from flaskr.forms import SearchForm


@app.route("/")
@app.route("/index")
@app.route("/home")
def home():
    form = SearchForm()
    return render_template('home.html', form=form, status=True, index=True, now=datetime.utcnow())


@app.route('/info')
def show_collections_info():
    from .src.data_action import get_registers_info, check_is_expired
    db = mongo[os.getenv('MONGO_INITDB_DATABASE')]
    service_collection = db['ServiceCollection']
    registers_info = get_registers_info(service_collection)
    expiration = check_is_expired(service_collection)
    return render_template('info.html', result=registers_info, isExpired=expiration, now=datetime.utcnow())


@app.route('/result', methods=['POST', 'GET'])
def show_search_results():
    from .src.data_action import search_into_collection
    form = SearchForm()
    if form.validate_on_submit():
        search_string = form.search.data
        db = mongo[os.getenv('MONGO_INITDB_DATABASE')]
        # call search methods
        result_missing_persons = search_into_collection(db['MissingPersons'], search_string)
        result_wanted_persons = search_into_collection(db['WantedPersons'], search_string)
        result_debtors = search_into_collection(db['Debtors'], search_string)
        result_lustrated = search_into_collection(db['Lustrated'], search_string)
        return render_template('result.html', now=datetime.utcnow(), result_MissingPersons=result_missing_persons,
                               result_WantedPersons=result_wanted_persons, result_Debtors=result_debtors,
                               result_Lustrated=result_lustrated)
