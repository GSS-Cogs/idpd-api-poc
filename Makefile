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
