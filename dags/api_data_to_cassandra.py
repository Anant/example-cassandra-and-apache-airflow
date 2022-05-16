
from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.apache.cassandra.hooks.cassandra import CassandraHook
from cassandra.cluster import Cluster
from uuid import uuid1
import json
import requests
import pprint

cassandra_hook = CassandraHook("cassandra_default")
pp = pprint.PrettyPrinter(indent=4)

dag = DAG("Airflow_and_Cassandra",
    description="A simple DAG that help to process data from API and send data to Cassandra Database",
    schedule_interval=None,
    start_date=datetime(2021, 1, 1),
    catchup=False,
    tags=["ETL_jobs"])

def get_rest_api_data(**context):
    task_instance = context["ti"]

    params = dict()
    base_url = "http://api.mediastack.com/v1/news"
    params["access_key"] = "YOUR_API_KEY"
    params['sources'] = "cnn,bbc" 

    response_from_api = requests.get(base_url, params=params)
    json_data = json.loads(response_from_api.text)
    task_instance.xcom_push("json_data", json_data)


def save_json_to_file(**context):
    task_instance = context["ti"]
    data_from_api = task_instance.xcom_pull(task_ids='get_rest_api_data', 
                                            key='json_data'
                                            )
    data_to_write = json.dumps(data_from_api)
    with open("/tmp/api_data.json", "w") as data_file:
        data_file.write(data_to_write)


def upload_to_s3(filename: str, key: str, bucket_name: str) -> None:
    hook = S3Hook('news_s3_bucket')
    hook.load_file(filename=filename, key=key, bucket_name=bucket_name, replace=True)

def insert_into_cassandra_db(**context):
    task_instance = context["ti"]
    Live_News_data = task_instance.xcom_pull(task_ids='get_rest_api_data', 
                                            key='json_data'
                                            )
    cluster = Cluster(['127.0.0.1'], port = 9042)
    session = cluster.connect('news')

    for i in range(0, len(Live_News_data['data'])):
        session.execute(
        """
        INSERT INTO news.news_table (uuiid, author, title, description, url, source, image, category, language, country, published_at)
        VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s,  %s )
        """,(uuid1(), Live_News_data['data'][i]["author"], Live_News_data['data'][i]["title"], 
        Live_News_data['data'][i]["description"], Live_News_data['data'][i]["url"], 
        Live_News_data['data'][i]["source"], Live_News_data['data'][i]["image"],
        Live_News_data['data'][i]["category"], Live_News_data['data'][i]["language"], 
        Live_News_data['data'][i]["country"], Live_News_data['data'][i]["published_at"],
        )
        )
        print("Done Sending : ->",Live_News_data['data'][i])


git_pull = BashOperator(
        task_id="pull_github_repo",
        bash_command="scripts/pull_github_repo.sh",
        dag=dag,
    )

get_data_from_api = PythonOperator( 
    task_id="get_rest_api_data", 
    python_callable=get_rest_api_data, 
    dag=dag
    )

save_data_locally = PythonOperator(
    task_id="save_json_to_file",
    python_callable=save_json_to_file, 
    dag=dag,
    )

upload_file_to_s3 = PythonOperator(
    task_id='upload_to_s3',
    python_callable=upload_to_s3,
    op_kwargs={
        'filename': "/tmp/api_data.json",
        'key': 'api_data.json',
        'bucket_name': 'anantworkflowresult',
    }, 
    dag=dag,)

insert_into_cassandra = PythonOperator(
    task_id="cassandra_inserts",
    python_callable=insert_into_cassandra_db,
    dag=dag,
)


git_pull >> get_data_from_api >> save_data_locally >> [upload_file_to_s3, insert_into_cassandra]
