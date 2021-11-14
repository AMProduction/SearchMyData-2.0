import logging
from flask import Flask, render_template, request


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)

    @app.route('/')
    def home():
        return render_template('home.html', status=True)

    @app.route('/info')
    def getCollectionsInfo():
        from .src.ServiceTools import ServiceTools
        serviceTool = ServiceTools()
        registersInfo = serviceTool.getRegistersInfo()
        expiration = serviceTool.checkIsExpired()
        return render_template('info.html', result=registersInfo, isExpired=expiration)

    @app.route('/result', methods=['POST', 'GET'])
    def getSearchResults():
        from .src.DebtorsRegister import DebtorsRegister
        from .src.EntrepreneursRegister import EntrepreneursRegister
        from .src.LegalEntitiesRegister import LegalEntitiesRegister
        from .src.MissingPersonsRegister import MissingPersonsRegister
        from .src.WantedPersonsRegister import WantedPersonsRegister
        # create instances
        missingPersons = MissingPersonsRegister()
        wantedPersons = WantedPersonsRegister()
        debtors = DebtorsRegister()
        legalEntities = LegalEntitiesRegister()
        entrepreneurs = EntrepreneursRegister()
        if request.method == 'POST':
            searchString = request.form['search']
            # call search methods
            resultMissingPersons = missingPersons.searchIntoCollection(
                searchString)
            resultWantedPersons = wantedPersons.searchIntoCollection(
                searchString)
            resultDebtors = debtors.searchIntoCollection(searchString)
            resultLegalEntities = legalEntities.searchIntoCollection(
                searchString)
            resultEntrepreneurs = entrepreneurs.searchIntoCollection(
                searchString)
            return render_template('result.html', resultMissingPersons=resultMissingPersons, resultWantedPersons=resultWantedPersons, resultDebtors=resultDebtors, resultLegalEntities=resultLegalEntities, resultEntrepreneurs=resultEntrepreneurs)

    return app
