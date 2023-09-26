# idpd-api-poc
A proof of concept API layer to manage content negotiation across IDPD resources and provide an abstraction to 3rd party data services.

## Usage

This application uses [pipenv](https://pypi.org/project/pipenv/) to manage dependencies.

### development

Install dependencies via `pipenv sync --dev`

Run the server via `pipenv run uvicorn src.main:app --reload`

### Testing

The unit tests are made with pytest and to run the tests use command: `pipenv run pytest`.
