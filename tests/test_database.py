#  Copyright (c) 2023 Andrii Malchyk, All rights reserved.

import pytest


class TestDatabase:

    def test_service_collection(self, database_connect):
        db = database_connect
        service_col = db['ServiceCollection']
        documents_count = service_col.count_documents({})
        assert documents_count > 0

    @pytest.mark.missingpersons
    def test_missing_persons_collection(self, database_connect):
        db = database_connect
        missing_persons_col = db['MissingPersons']
        documents_count = missing_persons_col.count_documents({})
        assert documents_count > 0

    @pytest.mark.wantedpersons
    def test_wanted_persons_collection(self, database_connect):
        db = database_connect
        wanted_persons_col = db['WantedPersons']
        documents_count = wanted_persons_col.count_documents({})
        assert documents_count > 0

    @pytest.mark.debtors
    def test_debtors_collection(self, database_connect):
        db = database_connect
        debtors_col = db['Debtors']
        documents_count = debtors_col.count_documents({})
        assert documents_count > 0

    def test_entrepreneurs_collection(self, database_connect):
        db = database_connect
        entrepreneurs_col = db['Entrepreneurs']
        documents_count = entrepreneurs_col.count_documents({})
        assert documents_count > 0

    @pytest.mark.legalentities
    def test_legal_entities_collection(self, database_connect):
        db = database_connect
        legal_entities_col = db['LegalEntities']
        documents_count = legal_entities_col.count_documents({})
        assert documents_count > 0

    @pytest.mark.lustrated
    def test_lustrated_collection(self, database_connect):
        db = database_connect
        legal_entities_col = db['Lustrated']
        documents_count = legal_entities_col.count_documents({})
        assert documents_count > 0
