from airflow import DAG
from datetime import datetime,timedelta
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'woodzee',
    'retries': 5,
    'retry_delay': timedelta(minutes=5)
}


def greet(name, age):
    print(f"Hello World! My name is {name}, and I am {age} years old.")
    

with DAG(
    dag_id='dag_with_python_operator',
    default_args = default_args,
    description='My first DAG using python operator.',
    start_date=datetime(2021,10,6),
    schedule_interval='@daily'

) as dag:

    task1 = PythonOperator(
        task_id='greet',
        python_callable=greet,
        op_kwargs={'name': 'Tom', 'age': 20}
    )

    task1