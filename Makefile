PYTHON ?= python3

.PHONY: build lint test validate benchmark ci

build:
	$(PYTHON) scripts/validate_repo_contracts.py --mode build

lint:
	$(PYTHON) scripts/validate_repo_contracts.py --mode lint

test:
	$(PYTHON) scripts/validate_repo_contracts.py --mode test

validate:
	$(PYTHON) scripts/validate_repo_contracts.py --mode validate

benchmark:
	$(PYTHON) scripts/benchmark_contract_dry_run.py

ci: validate benchmark
