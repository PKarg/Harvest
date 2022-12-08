FROM python:3.10-slim

LABEL maintainer="pkargulewicz"

ENV PYTHONUNBUFFERED 1

RUN apt-get update
RUN apt-get install python3-dev default-libmysqlclient-dev gcc  -y

RUN adduser --disabled-password --gecos '' user
USER user

RUN mkdir /home/user/Harvest

WORKDIR /home/user/Harvest
COPY ./ /home/user/Harvest

COPY ./requirements.txt /home/user/Harvest/requirements.txt

RUN pip install -r /home/user/Harvest/requirements.txt
