# idpd-api-poc
A proof of concept API layer to manage content negotiation across IDPD resources and provide an abstraction to 3rd party data services.

## Usage

This application uses [pipenv](https://pypi.org/project/pipenv/) to manage dependencies.

### development

Run `pipenv run python3 ./app/hello_app.py`. This wil run the app with browser based exceptions and _hot reloading_ enabled.

### production

Running the app in production is handled via the Dockerfile which installs all dependent packages (outlined in the pipfile.lock) into its base python version and runs the app via [gunicorn](https://gunicorn.org/).

### via gunicorn locally

To run via this mechanism locally (for example, if you want to trial some [gunicorn](https://gunicorn.org/) settings) do the following:

- `pipenv shell` to activate the virtual environment
- `cd app`
- `gunicorn --bind 0.0.0.0:5000 wsgi:app`

Note: This is slightly different than how the Dockerfile accomplishes the same thing, but its purely to avoid people installing this apps dependencies directly into their base interpreter locally which might interfere with running other things (a consideration an image does not have).


### Testing

The unit tests are made with pytest and to run the tests use command: `pipenv run pytest` thiss will run the `test_dataset.py` file and run all tests in it.
