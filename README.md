# Apache Airflow and Apache Cassandra

This repository contains the Airflow DAG that extract news data from a Live API data. The extracted data is processed and the data is loaded into Apache Cassandra database. We have used the Airflow-cassandra provider to load our data into the Cassandra database. 

We have provided two different scripts that help to install Airflow using Docker container and using the Python PIP, you can just start the bash scripts using `./airflow_pip_installer.sh`.

The CQL script for our database setup is in the file execute.cql. You can use automation to copy this file into the Cassandra docker container and create your databases using Airflow as the orchestrator. Also, it is very important to note that we have decided not to look into how to setup Cassandra on the Docker container, but You can learn how to do this here [Cassandra on Docker](https://blog.anant.us/cassandra-launch-70-basics-of-apache-cassandra/).

With that, let's setup Airflow on the docker container. 
### Clone the repo
```
git clone https://github.com/Anant/example-cassandra-and-apache-airflow.git
```
### Build the Airflow image with additional dependencies
```
docker build . -f Dockerfile --tag <ImageName>
```
### Start, and run the containers with the command below
```
docker-compose up -d
```
### Start the bash script to install Airflow CLI
```
./airflow.sh
```
### Confirm that Airflow is running [localhost:8080](http://localhost:8080/)
Now navigate to the DAGs page and run the Airflow_and_Cassandra DAG, start building your own DAG. You can read more about this here [Airflow and Casssandra](https://blog.anant.us/airflow-and-cassandra-writing-to-cassandra-from-airflow/).

