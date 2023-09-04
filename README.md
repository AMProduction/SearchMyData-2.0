# Welcome to the SearchMyData-2.0 App! The web version of [the SearchMyData App](https://github.com/AMProduction/SearchMyData/wiki)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![CodeQL](https://github.com/AMProduction/SearchMyData-2.0/actions/workflows/github-code-scanning/codeql/badge.svg?branch=main)](https://github.com/AMProduction/SearchMyData-2.0/actions/workflows/github-code-scanning/codeql) [![Build and Push Docker Image to Docker Hub](https://github.com/AMProduction/SearchMyData-2.0/actions/workflows/docker-hub.yml/badge.svg)](https://github.com/AMProduction/SearchMyData-2.0/actions/workflows/docker-hub.yml) ![Docker Image Version (latest semver)](https://img.shields.io/docker/v/andruxa17/searchmydata2) ![Docker Image Size with architecture (latest by date/latest semver)](https://img.shields.io/docker/image-size/andruxa17/searchmydata2)

![Apache Airflow](https://img.shields.io/badge/Apache%20Airflow-017CEE?style=for-the-badge&logo=Apache%20Airflow&logoColor=white) ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white) ![MongoDB](https://img.shields.io/badge/MongoDB-%234ea94b.svg?style=for-the-badge&logo=mongodb&logoColor=white) ![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white) ![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)

## Description

The app gives the possibility to perform a search into the Ukrainian
government [Open data portal](https://data.gov.ua/en/) datasets.  
At this moment (September 2023)
integrated [Information on missing citizens](https://data.gov.ua/en/dataset/470196d3-4e7a-46b0-8c0c-883b74ac65f0),
[Information about people hiding from the authorities](https://data.gov.ua/en/dataset/7c51c4a0-104b-4540-a166-e9fc58485c1b),
[Unified register of debtors](https://data.gov.ua/dataset/506734bf-2480-448c-a2b4-90b6d06df11e),
[Unified State Register of Legal Entities, Individual Entrepreneurs and Public Associations](https://data.gov.ua/dataset/1c7f3815-3259-45e0-bdf1-64dca07ddc10)
*(temporarily unavailable)*
and [Integrated Unified State Register of Lustrated Persons](https://data.gov.ua/dataset/8faa71c1-3a54-45e8-8f6e-06c92b1ff8bc).

## How to use

Use [docker-compose.yml](docker-compose.yml) to start services.  
The ENV variables:

- **FLASK_DEBUG**. `True` or `False`. The built-in Werkzeug development server provides a debugger which shows an
  interactive traceback in the browser when an unhandled error occurs during a request. This debugger should only be
  used during development.
- **FLASK_APP**. The environment variable is the name of the module to import at flask run. Usually `main.py`.
- *SECRET_KEY**. A secret key that will be used for securely signing the session cookie and can be used for any other
  security related needs by extensions or your application. It should be a long random `bytes` or `str`.
- **MONGO_URI**. The standard URI connection scheme.
- **MONGO_INITDB_DATABASE**. The DB name.
- **DOCUMENTS_PER_PAGE**. The count of search result records per page.
- **APP_NAME**. In our case `searchmydata2`.
- **TAG**. The app version `v2.2b`.

## Recommended Operating Systems

- **Windows:** 10 or newer
- **MAC:** OS X v10.7 or higher
- **Linux**

## Hardware requirements

- **Processor:** 2 gigahertz (GHz) or faster processor or SoC
- **RAM:** 8+ GB
- **SSD**

## Prerequisites

[Docker](https://www.docker.com)

[**Airflow**](https://airflow.apache.org) is tested with:

- [Python](https://www.python.org): 3.8, 3.9, 3.10, 3.11
- Databases:
    - PostgreSQL: 11, 12, 13, 14, 15
    - MySQL: 5.7, 8
    - SQLite: 3.15.0+
    - MSSQL(Experimental): 2017, 2019
- Kubernetes: 1.23, 1.24, 1.25, 1.26, 1.27

## See additional info into [the SearchMyData-2.0 App wiki](https://github.com/AMProduction/SearchMyData-2.0/wiki)

***
Developed in [PyCharm](https://www.jetbrains.com/pycharm/) - The Python IDE for Professional Developers.  
License kindly provided by [JetBrains Community Support Team](https://www.jetbrains.com/community/opensource/#support)  
![JetBrains Logo (Main) logo](https://resources.jetbrains.com/storage/products/company/brand/logos/jb_beam.svg) ![PyCharm logo](https://resources.jetbrains.com/storage/products/company/brand/logos/PyCharm.svg) ![PyCharm logo](https://resources.jetbrains.com/storage/products/company/brand/logos/PyCharm_icon.svg)
