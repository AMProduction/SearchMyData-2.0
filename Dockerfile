# syntax=docker/dockerfile:1
FROM python:3.10.12-slim-bullseye
LABEL authors="andrii_malchyk"

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Create app directory
WORKDIR /searchmydata2

# Install app dependencies
COPY ./requirements.txt /searchmydata2/requirements.txt

RUN pip install --upgrade pip && pip install -r requirements.txt

# Bundle app source
COPY ./flask_app/ /searchmydata2/

ARG FLASK_DEBUG
ARG FLASK_APP
ARG SECRET_KEY
ARG MONGO_URI
ARG MONGO_INITDB_DATABASE

ENV FLASK_DEBUG=${FLASK_DEBUG}
ENV FLASK_APP=${FLASK_APP}
ENV SECRET_KEY=${SECRET_KEY}
ENV MONGO_URI=${MONGO_URI}
ENV MONGO_INITDB_DATABASE=${MONGO_INITDB_DATABASE}

# Creates a non-root user and adds permission to access the /app folder
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /searchmydata2
USER appuser

EXPOSE 5001
CMD [ "waitress-serve", "--host", "0.0.0.0", "--port", "5001", "main:app"]
