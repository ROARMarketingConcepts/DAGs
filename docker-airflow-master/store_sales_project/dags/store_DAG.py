from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.mysql_operator import MySqlOperator

from datacleaner import data_cleaner

default_args = {
	'owner': 'Airflow',
	'start_date': datetime(2023,8,28),
	'retries': 1,
	'retry_delay': timedelta(seconds=5)
	}

dag = DAG(
	'store_dag',
	default_args=default_args,
	schedule_interval='@daily',
    template_searchpath=['/usr/local/airflow/sql_files'],   # specify path to SQL scripts
	catchup=False
	)

# Task 1 - we need to check that the source file is present

t1 = BashOperator(
	task_id='check_source_file_exists',
	bash_command='shasum ~/store_files_airflow/raw_store_transactions.csv',
	retries=2,
	retry_delay=timedelta(seconds=15),
	dag=dag 
	)

# Task 2 - clean the source .csv file

t2 = PythonOperator(
    task_id='clean_raw_csv_file',
    python_callable=data_cleaner,
    dag=dag
	)

# Task 3 - create a table in MySQL

t3 = MySqlOperator(
    task_id='create_mysql_table', 
    mysql_conn_id='mysql_conn', 
    sql='create_table.sql',
    dag=dag
	)

t1 >> t2 >> t3
