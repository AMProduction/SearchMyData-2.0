#  Copyright (c) 2023 Andrii Malchyk, All rights reserved.
import os
from datetime import datetime

from flask import render_template, request, session
from flaskr import app, mongo
from flaskr.forms import SearchForm


@app.route("/")
@app.route("/index")
@app.route("/home")
def home():
    form = SearchForm()
    if 'search_string' in session:
        form.search.data = session['search_string']
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
    from .src.data_action import search_into_collection, get_pages_count
    form = SearchForm()
    if form.validate_on_submit():
        search_string = form.search.data
        session['search_string'] = search_string
    else:
        search_string = session['search_string']
    page = request.args.get('page', 0, type=int)
    db = mongo[os.getenv('MONGO_INITDB_DATABASE')]

    # call search methods
    result_count_missing_persons, result_missing_persons = search_into_collection(db['MissingPersons'], search_string,
                                                                                  page)
    pages_for_missing_persons = get_pages_count(result_count_missing_persons)
    result_count_wanted_persons, result_wanted_persons = search_into_collection(db['WantedPersons'], search_string,
                                                                                page)
    pages_for_wanted_persons = get_pages_count(result_count_wanted_persons)
    result_count_debtors, result_debtors = search_into_collection(db['Debtors'], search_string, page)
    pages_for_debtors = get_pages_count(result_count_debtors)
    result_count_lustrated, result_lustrated = search_into_collection(db['Lustrated'], search_string, page)
    pages_for_lustrated = get_pages_count(result_count_lustrated)

    pages_count = max(pages_for_lustrated, pages_for_debtors, pages_for_wanted_persons, pages_for_missing_persons)
    if page == 0:
        has_previous = False
    else:
        has_previous = True
    if page == pages_count - 1:
        has_next = False
    else:
        has_next = True
    return render_template('result.html', now=datetime.utcnow(), result_MissingPersons=result_missing_persons,
                           result_WantedPersons=result_wanted_persons, result_Debtors=result_debtors,
                           result_Lustrated=result_lustrated, pages_count=pages_count, has_next=has_next,
                           has_previous=has_previous, page=page,
                           result_count_missing_persons=result_count_missing_persons,
                           result_count_wanted_persons=result_count_wanted_persons,
                           result_count_debtors=result_count_debtors, result_count_lustrated=result_count_lustrated)
