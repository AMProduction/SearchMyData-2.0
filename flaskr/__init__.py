from flask import Flask, render_template, request


def create_app():
    # create and configure the app
    app = Flask(__name__)

    @app.route('/')
    def home():
        return render_template('home.html', status=True)

    @app.route('/info')
    def get_collections_info():
        from .src.ServiceTools import ServiceTools
        service_tool = ServiceTools()
        registers_info = service_tool.get_registers_info()
        expiration = service_tool.check_is_expired()
        return render_template('info.html', result=registers_info, isExpired=expiration)

    @app.route('/result', methods=['POST', 'GET'])
    def get_search_results():
        from .src.DebtorsRegister import DebtorsRegister
        from .src.EntrepreneursRegister import EntrepreneursRegister
        from .src.LegalEntitiesRegister import LegalEntitiesRegister
        from .src.MissingPersonsRegister import MissingPersonsRegister
        from .src.WantedPersonsRegister import WantedPersonsRegister
        # create instances
        missing_persons = MissingPersonsRegister()
        wanted_persons = WantedPersonsRegister()
        debtors = DebtorsRegister()
        legal_entities = LegalEntitiesRegister()
        entrepreneurs = EntrepreneursRegister()
        if request.method == 'POST':
            search_string = request.form['search']
            # call search methods
            result_missing_persons = missing_persons.search_into_collection(search_string)
            result_wanted_persons = wanted_persons.search_into_collection(search_string)
            result_debtors = debtors.search_into_collection(search_string)
            result_legal_entities = legal_entities.search_into_collection(search_string)
            result_entrepreneurs = entrepreneurs.search_into_collection(search_string)
            return render_template('result.html', resultMissingPersons=result_missing_persons,
                                   resultWantedPersons=result_wanted_persons, resultDebtors=result_debtors,
                                   resultLegalEntities=result_legal_entities, resultEntrepreneurs=result_entrepreneurs)

    return app
