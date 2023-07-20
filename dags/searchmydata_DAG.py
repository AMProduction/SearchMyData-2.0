#  Copyright (c) 2023 Andrii Malchyk, All rights reserved.

import pendulum

from airflow.decorators import dag, task
from airflow.models import Variable


@dag(dag_id='SearchMyData_ETL',
     schedule_interval='@daily',
     start_date=pendulum.datetime(2023, 7, 20, tz="UTC"),
     catchup=False,
     tags=["searchmydata"],
     max_active_runs=1,
     )
@task()
def extract_missing_person_register():
    connection_string = Variable.get("mongo_connection_string")
    from modules.MissingPersonsRegister import MissingPersonsRegister
    missing_persons = MissingPersonsRegister(connection_string)
    missing_persons.setup_dataset()


extract_missing_person_register()
