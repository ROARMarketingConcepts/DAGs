from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime,timedelta

default_args = {
    'owner': 'woodzee',
    'retries': 5,
    'retry_delay': timedelta(minutes=2)
}

with DAG(
    dag_id='my_first_dag',
    default_args = default_args,
    description='This is the first dag we have written.',
    start_date=datetime(2021,7,29,2),
    schedule_interval='@daily'

) as dag:
    
    task1 = BashOperator(
        task_id='first_task',
        bash_command="echo hello world, this is the first task!"
    )

    task2 = BashOperator(
        task_id='second_task',
        bash_command="echo hey, I am task 2 and I always run after task 1!"
    )

    task3 = BashOperator(
        task_id='third_task',
        bash_command="echo hey, I am task 3 and I always run after task 1 and at the same time as task2!"
    )

# We can show task dependencies in 1 of 3 ways:

# task1.set_downstream(task2)
# task1.set_downstream(task3)

# task1 >> task2
# task1 >> task3

task1 >> [task2, task3]