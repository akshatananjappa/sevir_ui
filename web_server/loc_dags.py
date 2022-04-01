# step - 1

from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.dummy_operator import DummyOperator

import random
from random import randint
from datetime import datetime

def loading_model():
    return randint(1, 10)

#function to run every hour
def run_model_hourly():
    return randint(1, 50)

def save_image():
    return randint(1, 50)


# step - 2

default_arg_values = {
    'owner' : 'airflow',
    'depends_on_past' : False,
    'start_date' : datetime(2022, 3, 30),
    'retries' : 0
}

# step - 3

with DAG("DAG-3", default_args=default_arg_values, schedule_interval="@hourly", catchup=False) as dag:

# step - 4
   
    visualize_model = PythonOperator(
        task_id = "visualize_model",
        python_callable = run_model_hourly
    )

    load_model = PythonOperator(
        task_id = "loading_model",
        python_callable = loading_model
    )

    save_images = BashOperator(
        task_id = "save_image",
        bash_command = "echo 'save_image'"
    )

    start = DummyOperator(
        task_id='start',
        dag=dag
    )

    end = DummyOperator(
        task_id='end',
        dag=dag
    )


# step - 5

start >> load_model >> visualize_model >> save_images >> end