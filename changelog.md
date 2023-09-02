## v2.0

### The main pull requests

- https://github.com/AMProduction/SearchMyData-2.0/pull/16
- https://github.com/AMProduction/SearchMyData-2.0/pull/18
- https://github.com/AMProduction/SearchMyData-2.0/pull/23
- https://github.com/AMProduction/SearchMyData-2.0/pull/25

### The main changes

- Migration to [Flask](https://flask.palletsprojects.com/en/2.3.x/)
- UI improvements
- Refactoring to implement [PEP 8](https://peps.python.org/pep-0008/)
- Update [the issue templates](.github/ISSUE_TEMPLATE)
- Create [CODE_OF_CONDUCT.md](docs/CODE_OF_CONDUCT.md)
- Search results save to PDF via [html2pdf](https://www.npmjs.com/package/html2pdf.js/v/0.10.1) library
- The [docker-compose.yml](docker-compose.yml) added
- Migrated to [Airflow](https://airflow.apache.org)
- Refactoring ETL pipeline
- Create [SECURITY.md](docs/SECURITY.md)
- Doc strings updated
- Refactored get_collections_info() function
- Dynamic display year in the footer of the pages
- Read the DB connection string from the .env file
- HTML structure changed
- Refactored search results representation
- Code beautification
- Added [CSRF](https://wtforms.readthedocs.io/en/2.3.x/csrf/) app protection
- Added [WTForms](https://wtforms.readthedocs.io/en/2.3.x/) support

***

## v2.1a

### The main pull requests

- https://github.com/AMProduction/SearchMyData-2.0/pull/26
- https://github.com/AMProduction/SearchMyData-2.0/pull/27
- https://github.com/AMProduction/SearchMyData-2.0/pull/28

### The main changes

- [Dockerfile](Dockerfile) added
- The [docker-compose.yml](docker-compose.yml) modified
- Added [GitHub actions](.github/workflows/docker-hub.yml) to build and push images
  to [Docker hub](https://hub.docker.com/repository/docker/andruxa17/searchmydata2/general)
- Return documents per page and page numbers
- Added the paginations to the template
- Added process page_number from the URL
- Added processing NEXT and PREVIOUS buttons
- Docstring updated. Added documents found count. SearchForm modified
- Added saving the search query to the session variable

***

## v2.2b

### The main pull requests

- https://github.com/AMProduction/SearchMyData-2.0/pull/31

### The main changes

- Create [PULL_REQUEST_TEMPLATE.md](docs/PULL_REQUEST_TEMPLATE.md)
- Create [CONTRIBUTING.md](docs/CONTRIBUTING.md)
- Refactored the service collection processing
- Added: debtors_model, lustrated_persons_model, missing_persons_model, wanted_persons_model
- Added mapping for ObjectID field in the models. Added processing Missing Persons register
  through [the ORM](http://mongoengine.org)
- Added processing all registers through [the ORM](http://mongoengine.org)
- Refactored /result route
- Change import in routes.py
- Code prettified
- [readme.md](README.md) updated
- [changelog.md](changelog.md) added