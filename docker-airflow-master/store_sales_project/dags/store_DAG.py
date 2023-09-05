from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.mysql_operator import MySqlOperator
from airflow.operators.email_operator import EmailOperator

from datacleaner import data_cleaner

yesterday_date = datetime.strftime(datetime.now()-timedelta(1), '%Y-%m-%d')

default_args = {
	'owner': 'Airflow',
	'start_date': datetime(2023,8,28),
	'retries': 1,
	'retry_delay': timedelta(seconds=5)
	}

# dag = DAG(
# 	'store_dag',
# 	default_args=default_args,
# 	schedule_interval='@daily',
#     template_searchpath=['/usr/local/airflow/sql_files'],   # specify path to SQL scripts
# 	catchup=False
# 	)

with DAG(
	'store_dag',
	default_args=default_args,
	schedule_interval='@daily',
    template_searchpath=['/usr/local/airflow/sql_files'],   # specify path to SQL scripts
	catchup=False
	) as dag:

# Task 1 - we need to check that the source file is present

    t1 = BashOperator(
        task_id='check_source_file_exists',
        bash_command='shasum ~/store_files_airflow/raw_store_transactions.csv',
        retries=2,
        retry_delay=timedelta(seconds=15),
        # dag=dag 
        )

# Task 2 - clean the source .csv file

    t2 = PythonOperator(
        task_id='clean_raw_csv_file',
        python_callable=data_cleaner,
        # dag=dag
        )

# Task 3 - create a table in MySQL

    t3 = MySqlOperator(
        task_id='create_mysql_table', 
        mysql_conn_id='mysql_conn', 
        sql='create_table.sql',
        # dag=dag
        )

# Task 4 - insert store sales data into the SQL table

    t4 = MySqlOperator(
        task_id='insert_into_mysql_table', 
        mysql_conn_id='mysql_conn', 
        sql='insert_into_table.sql',
        # dag=dag
        )

# Task 5 - Query the SQL table

    t5 = MySqlOperator(
        task_id='select_from_mysql_table', 
        mysql_conn_id='mysql_conn', 
        sql='select_from_table.sql',
        # dag=dag
        )

# Task 6 - index SQL query output file for 'location_wise_profit.csv' by date

    t6 = BashOperator(
        task_id='move_file1', 
        bash_command='cat ~/store_files_airflow/location_wise_profit.csv && mv ~/store_files_airflow/location_wise_profit.csv ~/store_files_airflow/location_wise_profit_%s.csv' % yesterday_date,
        # dag=dag
        )

# Task 7 - index SQL query output file for 'store_wise_profit.csv' by date

    t7 = BashOperator(
        task_id='move_file2', 
        bash_command='cat ~/store_files_airflow/store_wise_profit.csv && mv ~/store_files_airflow/store_wise_profit.csv ~/store_files_airflow/store_wise_profit_%s.csv' % yesterday_date,
        # dag=dag
        )

# Task 8 - Send e-mail to stakeholder with profit files attached

    t8 = EmailOperator(
        task_id='send_email',
        to='ken@roarmarketingconcepts.com',
        subject='Daily report generated',
        html_content=""" <h1>Congratulations! Your store reports are ready!</h1> """,
        files=['/usr/local/airflow/store_files_airflow/location_wise_profit_%s.csv' % yesterday_date, '/usr/local/airflow/store_files_airflow/store_wise_profit_%s.csv' % yesterday_date],
        # dag=dag
        )

# Task 9 - Rename new 'raw_store_transactions' data file from stakeholders

    t9 = BashOperator(
        task_id='rename_raw_csv_file', 
        bash_command='mv ~/store_files_airflow/raw_store_transactions.csv ~/store_files_airflow/raw_store_transactions_%s.csv' % yesterday_date,
        # dag=dag
        )

    t1 >> t2 >> t3 >> t4 >> t5 >> [t6,t7] >> t8 >> t9

