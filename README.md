# idpd-api-poc
A proof of concept API layer to manage content negotiation across IDPD resources and provide an abstraction to 3rd party data services

## Usage

- development mode: `pipenv run python3 ./app/hello_world.py` (this enables browser based exceptions and debugging)
- productiond mode: `gunicorn --bind 0.0.0.0:5000 wsgi:app`
