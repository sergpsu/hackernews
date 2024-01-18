FROM python:3.11-slim
#FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONPATH=/app

RUN apt-get update -y
RUN apt-get install -y python3-pip


COPY ./app /app
COPY ./scripts /scripts
COPY ./requirements.txt /tmp

WORKDIR /app

RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

EXPOSE 22
EXPOSE 80

CMD ["sleep", "infinity"]
