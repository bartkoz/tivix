FROM python:3.8.7-slim

ENV PYTHONUNBUFFERED 1
ENV PIPENV_SYSTEM 1
ENV PYTHONPATH /opt/app


COPY requirements.txt /opt/app/
WORKDIR /opt/app
RUN pip install -r requirements.txt

COPY . /opt/app
