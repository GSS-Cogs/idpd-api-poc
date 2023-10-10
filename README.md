# idpd-api-poc
A proof of concept API layer to manage content negotiation across IDPD resources and provide an abstraction to 3rd party data services.

## Usage

This application uses [pipenv](https://pypi.org/project/pipenv/) to manage dependencies.

### Development

Install dependencies via `pipenv sync --dev`

Run the server via `pipenv run uvicorn src.main:app --reload`

If you want to browse the api content in your web browser (while developing only) then

```
export LOCAL_BROWSE_API=true
```

To turn this off `unset LOCAL_BROWSE_API`.

There is a `Makefile` with some useful development helpers:

- `make test` to run the unit tests.
- `make fmt` to format and lint your code.

### Oxigraph

#### Running Oxigraph Locally

- run [oxigraph]() locally via `docker-compose up -d` (from the root of this directory) which runs oxigraph as a detached (in the background) container on http://localhost:7878.
- use `docker-compose down` to turn it off.
- data will be persisted in the `./data` directory. To start over delete this directory after
you `docker-compose down` and start again.

#### Populating Oxigraph

- Make sure you've installed dev dependencies via `pipenv sync --dev`
- run `pipenv run python3 ./devdata/create_devdata.py`

This will populate `./devdata/out` with ttl files created from the jsonld samples
used to power the stubbed metadata store.

Each "item" in each stubbed store will have its own file RDF (.ttl) file but **the critical file** is "seed.trig" which will be all the RDF representing all the other ttl files combined and organised into **distinct named graphs** - this file will be what's loaded into the oxigraph.

To sanity check go to [http://localhost:7878/](http://localhost:7878/) and query against one of the named graphs, example:

```
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX ons: <https://data.ons.gov.uk/ns#>
PREFIX vcard: <http://www.w3.org/2006/vcard/ns#>

SELECT * FROM <https://data.ons.gov.uk/datasets/cpih/record> WHERE {
            ?s ?p ?o
        }
```

Where the _named graph_ is `https://data.ons.gov.uk/datasets/cpih/record` - you can get examples of others from your "seed.trig" file.

### Testing

The unit tests are made with pytest and to run the tests use command: `pipenv run pytest`.

**Note:** - you'll need to first shut down any local oxigraph container you have running first as the tests need to spin one up using that same port.