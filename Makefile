PYTHON ?= python3

.PHONY: build lint test validate benchmark benchmark-claim benchmark-repro ci

build:
	$(PYTHON) scripts/validate_repo_contracts.py --mode build

lint:
	$(PYTHON) scripts/validate_repo_contracts.py --mode lint

test:
	$(PYTHON) scripts/validate_repo_contracts.py --mode test
	$(PYTHON) scripts/python_importer_conformance.py --mode test
	$(PYTHON) scripts/rust_importer_conformance.py --mode test
	$(PYTHON) scripts/scir_bootstrap_pipeline.py --mode test

validate:
	$(PYTHON) scripts/run_repo_validation.py

benchmark:
	$(PYTHON) scripts/benchmark_contract_dry_run.py

benchmark-claim:
	$(PYTHON) scripts/benchmark_contract_dry_run.py --claim-run

benchmark-repro:
	$(PYTHON) scripts/benchmark_repro.py --run-id $(RUN_ID)

ci: validate benchmark
