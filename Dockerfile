FROM ubuntu:18.04

RUN apt-get update -y && apt-get install -y python3-pip python3-dev git gcc g++ dos2unix

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
RUN pip install pytest-docker-compose

COPY . /app

RUN dos2unix run-pipeline.sh && apt-get --purge remove -y dos2unix
RUN chmod +x run-pipeline.sh
RUN dos2unix run_test.sh && apt-get --purge remove -y dos2unix
RUN chmod +x run_test.sh

ENTRYPOINT ["sh"]