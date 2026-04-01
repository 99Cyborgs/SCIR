PYTHON ?= python3

.PHONY: build lint test validate benchmark ci

build:
	$(PYTHON) scripts/validate_repo_contracts.py --mode build

lint:
	$(PYTHON) scripts/validate_repo_contracts.py --mode lint

test:
	$(PYTHON) scripts/validate_repo_contracts.py --mode test
	$(PYTHON) scripts/python_importer_conformance.py --mode test
	$(PYTHON) scripts/scir_bootstrap_pipeline.py --mode test
	$(PYTHON) scripts/rust_importer_conformance.py --mode test
	$(PYTHON) scripts/scir_bootstrap_pipeline.py --language rust --mode test

validate:
	$(PYTHON) scripts/validate_repo_contracts.py --mode validate
	$(PYTHON) scripts/python_importer_conformance.py --mode validate-fixtures
	$(PYTHON) scripts/typescript_importer_conformance.py --mode validate-fixtures
	$(PYTHON) scripts/scir_bootstrap_pipeline.py --mode validate
	$(PYTHON) scripts/rust_importer_conformance.py --mode validate-fixtures
	$(PYTHON) scripts/scir_bootstrap_pipeline.py --language rust --mode validate

benchmark:
	$(PYTHON) scripts/benchmark_contract_dry_run.py

ci: validate benchmark
