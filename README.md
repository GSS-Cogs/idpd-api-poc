# idpd-api-poc
A proof of concept API layer to manage content negotiation across IDPD resources and provide an abstraction to 3rd party data services.

## Usage

This application uses [pipenv](https://pypi.org/project/pipenv/) to manage dependencies.

### Development

Install dependencies via `pipenv sync --dev`

Run the server via `make start`

If you want to browse the api content in your web browser (while developing only) then

```
export LOCAL_BROWSE_API=true
```

This will allow browser traffic despite mimetypes and will replace all `staging.idpd.uk` values with `localhost:8000` to allow click through navigation.

To turn this off `unset LOCAL_BROWSE_API`.

There is a `Makefile` with some useful development helpers:

- `make test` to run the unit tests.
- `make fmt` to format and lint your code.
- `make data` to create `./out/seed.ttl` with data for the graph.
- `make populate` to populate a local oxigraph where one is running.
- `make configure_dev` to enable client side git hooks for code quality (see following section).
- `make start` to start the api.

You can also just use a naked `make` to see your options.

**Note:** - with `make test` you'll need to first shut down any local oxigraph container you have running first as the tests currently spin one up using that same port.

### Git Hooks

This respisitory comes with two _client side_ git hooks for code quality:

- pre-commit - runs black, isort and the ruff linter on your code
- pre-push - runs unit tests before pushing code to a remote branch

You can enable these via `make configure_dev`, you need to do this once (per fresh clone of this repo).

PR's to this codebase are required to have correct formatting and have passing unit tests, so if you don't use git hooks be sure to run these processes manually.

### Oxigraph

#### Running Oxigraph Locally

- run [oxigraph]() locally via `docker-compose up -d` (from the root of this directory) which runs oxigraph as a detached (in the background) container on http://localhost:7878.
- use `docker-compose down` to turn it off.
- data will be persisted in the `./data` directory. To start over delete this directory after
you `docker-compose down` and start again.

#### Populating Oxigraph

- Make sure you've installed dev dependencies via `pipenv sync --dev`
- Set an env var to sepcify the graph you're using `export GRAPH_DB_URL=http://localhost:7878`
- run `make populate`

This will populate `./out` with ttl files created from the jsonld samples
used to power the stubbed metadata store.
