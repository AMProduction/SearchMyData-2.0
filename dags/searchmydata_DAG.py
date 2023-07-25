#  Copyright (c) 2023 Andrii Malchyk, All rights reserved.

import pendulum

from airflow.decorators import dag, task
from airflow.models import Variable
from airflow.operators.empty import EmptyOperator

connection_string = Variable.get("mongo_connection_string")


@dag(dag_id='SearchMyData_ETL',
     schedule_interval='@daily',
     start_date=pendulum.datetime(2023, 7, 20, tz="UTC"),
     catchup=False,
     tags=["searchmydata"],
     max_active_runs=1,
     )
def searchmydata_etl():
    start = EmptyOperator(task_id="start")
    stop = EmptyOperator(task_id="stop")

    @task()
    def extract_missing_persons_register():
        from modules.MissingPersonsRegister import MissingPersonsRegister
        missing_persons = MissingPersonsRegister(connection_string)
        missing_persons.setup_dataset()

    @task()
    def extract_wanted_persons_register():
        from modules.WantedPersonsRegister import WantedPersonsRegister
        wanted_persons = WantedPersonsRegister(connection_string)
        wanted_persons.setup_dataset()

    @task()
    def extract_debtors_register():
        from modules.DebtorsRegister import DebtorsRegister
        debtors = DebtorsRegister(connection_string)
        debtors.setup_dataset()

    @task()
    def extract_lustrated_persons_register():
        from modules.LustratedPersonsRegister import LustratedPersonsRegister
        lustrated = LustratedPersonsRegister(connection_string)
        lustrated.setup_dataset()

    start >> [extract_missing_persons_register(), extract_wanted_persons_register(),
              extract_lustrated_persons_register(), extract_debtors_register()] >> stop
    # start >> [extract_missing_persons_register(), extract_wanted_persons_register(),
    #           extract_lustrated_persons_register()] >> stop
    # start >> [extract_debtors_register()] >> stop


searchmydata_etl()
