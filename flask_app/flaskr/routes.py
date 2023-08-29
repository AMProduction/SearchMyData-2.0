#  Copyright (c) 2023 Andrii Malchyk, All rights reserved.
from datetime import datetime

from flask import render_template, request, session
from flaskr import app

from .forms import SearchForm


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
    from .src.data_action import check_is_expired, get_registers_info
    registers_info = get_registers_info()
    expiration = check_is_expired()
    return render_template('info.html', result=registers_info, isExpired=expiration, now=datetime.utcnow())


@app.route('/result', methods=['POST', 'GET'])
def show_search_results():
    from .src.data_action import get_search_result_count, search_into_collection, get_pages_count
    from .models.debtors_model import Debtor
    from .models.lustrated_persons_model import LustratedPerson
    from .models.missing_persons_model import MissingPerson
    from .models.wanted_persons_model import WantedPerson
    form = SearchForm()
    if form.validate_on_submit():
        search_string = form.search.data
        session['search_string'] = search_string
        session.pop('result_count_missing_persons', None)
        session.pop('result_count_wanted_persons', None)
        session.pop('result_count_debtors', None)
        session.pop('result_count_lustrated', None)
        session.pop('pages_count', None)
    else:
        search_string = session['search_string']
        result_count_missing_persons = session['result_count_missing_persons']
        result_count_wanted_persons = session['result_count_wanted_persons']
        result_count_debtors = session['result_count_debtors']
        result_count_lustrated = session['result_count_lustrated']
        pages_count = session['pages_count']

    session_variables = ['result_count_missing_persons', 'result_count_wanted_persons', 'result_count_debtors',
                         'result_count_lustrated', 'pages_count']
    if not any(variable in session_variables for variable in session):
        # get search result count
        result_count_missing_persons = get_search_result_count(MissingPerson, search_string)
        pages_for_missing_persons = get_pages_count(result_count_missing_persons)
        session['result_count_missing_persons'] = result_count_missing_persons

        result_count_wanted_persons = get_search_result_count(WantedPerson, search_string)
        pages_for_wanted_persons = get_pages_count(result_count_wanted_persons)
        session['result_count_wanted_persons'] = result_count_wanted_persons

        result_count_debtors = get_search_result_count(Debtor, search_string)
        pages_for_debtors = get_pages_count(result_count_debtors)
        session['result_count_debtors'] = result_count_debtors

        result_count_lustrated = get_search_result_count(LustratedPerson, search_string)
        pages_for_lustrated = get_pages_count(result_count_lustrated)
        session['result_count_lustrated'] = result_count_lustrated

        pages_count = max(pages_for_lustrated, pages_for_debtors, pages_for_wanted_persons, pages_for_missing_persons)
        session['pages_count'] = pages_count

    page = request.args.get('page', 0, type=int)

    # call search methods
    result_missing_persons = search_into_collection(MissingPerson, search_string, page)
    result_wanted_persons = search_into_collection(WantedPerson, search_string, page)
    result_debtors = search_into_collection(Debtor, search_string, page)
    result_lustrated = search_into_collection(LustratedPerson, search_string, page)

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
