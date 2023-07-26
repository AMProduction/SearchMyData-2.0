#  Copyright (c) 2023 Andrii Malchyk, All rights reserved.

import pendulum

from airflow.decorators import dag, task
from airflow.models import Variable
from airflow.operators.empty import EmptyOperator


@dag(dag_id='SearchMyData_ETL',
     schedule_interval='@daily',
     start_date=pendulum.datetime(2023, 7, 20, tz="UTC"),
     catchup=False,
     tags=["searchmydata"],
     max_active_runs=1,
     )
def searchmydata_etl():
    connection_string = Variable.get("mongo_connection_string")
    package_base_url = Variable.get("package_base_url")
    resource_base_url = Variable.get("resource_base_url")

    start = EmptyOperator(task_id="start")
    stop = EmptyOperator(task_id="stop")

    @task()
    def extract_missing_persons_register():
        from modules.MissingPersonsRegister import MissingPersonsRegister
        missing_persons_register_package_resource_id = Variable.get("missing_persons_register_package_resource_id")
        missing_persons = MissingPersonsRegister(connection_string, package_base_url, resource_base_url,
                                                 missing_persons_register_package_resource_id)
        missing_persons.setup_dataset()

    @task()
    def extract_wanted_persons_register():
        from modules.WantedPersonsRegister import WantedPersonsRegister
        wanted_persons_register_package_resource_id = Variable.get("wanted_persons_register_package_resource_id")
        wanted_persons = WantedPersonsRegister(connection_string, package_base_url, resource_base_url,
                                               wanted_persons_register_package_resource_id)
        wanted_persons.setup_dataset()

    @task()
    def extract_debtors_register():
        from modules.DebtorsRegister import DebtorsRegister
        debtors_register_package_resource_id = Variable.get("debtors_register_package_resource_id")
        debtors = DebtorsRegister(connection_string, package_base_url, resource_base_url,
                                  debtors_register_package_resource_id)
        debtors.setup_dataset()

    @task()
    def extract_lustrated_persons_register():
        from modules.LustratedPersonsRegister import LustratedPersonsRegister
        lustrated_persons_register_package_resource_id = Variable.get("lustrated_persons_register_package_resource_id")
        lustrated = LustratedPersonsRegister(connection_string, package_base_url, resource_base_url,
                                             lustrated_persons_register_package_resource_id)
        lustrated.setup_dataset()

    start >> [extract_missing_persons_register(), extract_wanted_persons_register(),
              extract_lustrated_persons_register(), extract_debtors_register()] >> stop


searchmydata_etl()
