.PHONY: all

# Help menu on a naked make
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

fmt: ## (Format) - runs black and isort against the codebase (auto triggered on pre-commit)
	pipenv run black ./src/*
	pipenv run isort ./src/*

lint: ## Run the ruff python linter (auto triggered on pre-commit)
	pipenv run ruff ./src/*

test: ## Run pytest and check test coverage (auto triggered on pre-push)
	pipenv run pytest --cov-report term-missing --cov=src --cov-config=./tests/coverage.rc

validate: ## Validate stub data files
	pipenv run python3 ./src/store/metadata/stub/validation.py

populate: ## Populate an oxigraph DB (that/if/when) one is running on localhost:7878
	pipenv run python3 ./src/data.py

data: ## Create source ttl seed file as ./out/seed.ttl but dont load it
	pipenv run python -c "from src.data import populate;populate(write_to_db=False)"

start: ## Start the api
	pipenv run uvicorn src.main:app --reload

configure_dev: ## Configure this repo for development purposes (activate hooks etc)
	cp ./hooks/pre-commit ./.git/hooks/pre-commit
	cp ./hooks/pre-push ./.git/hooks/pre-push
	chmod +x ./.git/hooks/pre-commit
	chmod +x ./.git/hooks/pre-push