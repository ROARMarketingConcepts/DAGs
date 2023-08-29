"""
Build a DAG that will create a new directory (let say 'test_dir') 
inside the dags folder, and crosscheck the results at task level.
"""
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2023, 8, 25),
    "email": ["airflow@airflow.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "directory": "test_dir"
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
}

dag = DAG("Assignment_1", 
        default_args=default_args, 
        schedule_interval=timedelta(1)
        )

# t1, t2 and t3 are examples of tasks created by instantiating operators
t1 = BashOperator(task_id="create_directory", bash_command="mkdir $directory", dag=dag)


templated_command = """
    if [ -d "$directory" ]; then
    echo "$directory does exist."
    fi
"""

t2 = BashOperator(
    task_id="check_directory",
    bash_command=templated_command,
    dag=dag,
)

t2.set_upstream(t1)
