from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.mysql_operator import MySqlOperator
from airflow.operators.email_operator import EmailOperator
from airflow.contrib.sensors.file_sensor import FileSensor

yesterday_date = datetime.strftime(datetime.now()-timedelta(1), '%Y-%m-%d')

default_args = {
	'owner': 'Airflow',
	'start_date': datetime(2023,9,10),
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
	'Assignment_2_DAG',
	default_args=default_args,
	schedule_interval='@daily',
    template_searchpath=['/usr/local/airflow/sql_files'],   # specify path to SQL scripts
	catchup=False
	) as dag:

# Task 1 - we need to check that the source file is present

    # t1 = BashOperator(
    #     task_id='check_source_file_exists',
    #     bash_command='shasum ~/store_files_airflow/raw_store_transactions.csv',
    #     retries=2,
    #     retry_delay=timedelta(seconds=15),
    #     # dag=dag 
    #     )

    t1 = FileSensor(
        task_id='check_hotel_file_exists',
        filepath='usr/local/airflow/data_files_airflow/hotel_bookings.csv',
        fs_conn_id='fs_default',
        poke_interval=10,
        timeout=150,
        soft_fail=True,
        # dag=dag 
        )

# Task 2 - clean the source .csv file

    # t2 = PythonOperator(
    #     task_id='clean_raw_csv_file',
    #     python_callable=data_cleaner,
    #     # dag=dag
    #     )

# Task 2 - create a table in MySQL

    t2 = MySqlOperator(
        task_id='create_mysql_table', 
        mysql_conn_id='mysql_conn', 
        sql='create_table.sql',
        # dag=dag
        )

# Task 3 - insert hotel bookings data into the SQL table

    t3 = MySqlOperator(
        task_id='insert_into_mysql_table', 
        mysql_conn_id='mysql_conn', 
        sql='insert_into_table.sql',
        # dag=dag
        )

# Task 4 - Query the SQL table

    t4 = MySqlOperator(
        task_id='select_from_mysql_table', 
        mysql_conn_id='mysql_conn', 
        sql='select_from_table.sql',
        # dag=dag
        )

# Task 5 - index SQL query output file for 'reservation_cancellations.csv' by date

    t5 = BashOperator(
        task_id='move_file1', 
        bash_command='cat ~/data_files_airflow/reservation_cancellations.csv && mv ~/data_files_airflow/reservation_cancellations.csv ~/data_files_airflow/reservation_cancellations_%s.csv' % yesterday_date,
        # dag=dag
        )

# # Task 7 - index SQL query output file for 'store_wise_profit.csv' by date

#     t7 = BashOperator(
#         task_id='move_file2', 
#         bash_command='cat ~/store_files_airflow/store_wise_profit.csv && mv ~/store_files_airflow/store_wise_profit.csv ~/store_files_airflow/store_wise_profit_%s.csv' % yesterday_date,
#         # dag=dag
#         )

# Task 6 - Send e-mail to stakeholder with profit files attached

    t6 = EmailOperator(
        task_id='send_email',
        to='ken@roarmarketingconcepts.com',
        subject='Reservation Cancellations report generated',
        html_content=""" <h1>Congratulations! Your cancellation reports are ready!</h1> """,
        files=['/usr/local/airflow/data_files_airflow/reservation_cancellations_%s.csv' % yesterday_date]
        )

# Task 7 - Rename new 'hotel_bookings.csv' data file from stakeholders

    t7 = BashOperator(
        task_id='rename_raw_csv_file', 
        bash_command='mv ~/data_files_airflow/hotel_bookings.csv ~/data_files_airflow/hotel_bookings_%s.csv' % yesterday_date,
        # dag=dag
        )

    t1 >> t2 >> t3 >> t4 >> t5 >> t6 >> t7

