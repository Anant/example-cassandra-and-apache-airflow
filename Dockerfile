FROM apache/airflow:2.2.5
USER root
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
         vim \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*
RUN apt-get update && \
  apt-get upgrade -y && \
  apt-get install -y git
USER airflow
RUN pip install --no-cache-dir lxml
RUN pip install --no-cache-dir apache-airflow-providers-docker==2.1.0
RUN pip install --no-cache-dir apache-airflow-providers-apache-cassandra==2.1.3
COPY --chown=airflow:root ./dags /opt/airflow/dags