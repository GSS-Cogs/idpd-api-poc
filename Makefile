.PHONY: all

# Help menu on a naked make
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

black: ## Run the black formatter against the codebase
	pipenv run black .

ruff: ## Run the ruff python linter
	pipenv run ruff .

fmt: black ruff ## "format", run black then the ruff linter

test: ## Run pytest and check test coverage
	pipenv run pytest --cov-report term-missing --cov=src --cov-config=./tests/coverage.rc ./tests/

populate: ## Populate an oxigraph DB at localhost:7878
	pipenv run python3 ./data.py

data: ## Create source ttl seed file as ./out/seed.ttl but dont load it
	pipenv run python -c "from data import populate;populate(write_to_db=False)"

start: ## Start the api
	pipenv run uvicorn src.main:app --reload