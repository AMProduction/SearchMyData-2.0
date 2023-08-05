# syntax=docker/dockerfile:1
FROM python:3.11.4-slim
LABEL authors="andrii_malchyk"

# Create app directory
WORKDIR /searchmydata2

# Install app dependencies
COPY ./requirements.txt /searchmydata2/requirements.txt

RUN pip install -r requirements.txt

# Bundle app source
COPY ./main.py /searchmydata2/main.py
COPY ./config.py /searchmydata2/config.py
COPY ./flaskr/ /searchmydata2/

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

EXPOSE 5000
CMD [ "flask", "run","--host","0.0.0.0","--port","5000"]
