from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta
import os

# Define constants
src_path = '/home/tfidf/PycharmProjects/corona/src/'

## Define the DAG object
default_args = {
    'owner': 'tfidf',
    'depends_on_past': False,
    'start_date': datetime(2020, 6, 9),    # The first date from which this DAG is valid
    'retries': 3,                           # Maximum retries per scheduled instance
    'retry_delay': timedelta(minutes=2),    # Waittime between retries
}
dag = DAG('corona_ETL', default_args=default_args, schedule_interval='0 15 * * *')

'''
Defining three tasks: one task to download S3 data
and two Spark jobs that depend on the data to be 
successfully downloaded
task to download data
'''
# Echo some text into a file
corona_ETL = BashOperator(
    task_id='echo_text',
    bash_command='python3 ' + src_path + 'ETL.py',
    dag=dag)
