PYTHON ?= python3

.PHONY: build lint test validate benchmark benchmark-claim benchmark-repro ci

build:
	$(PYTHON) scripts/run_repo_build.py

lint:
	$(PYTHON) scripts/run_repo_lint.py

test:
	$(PYTHON) scripts/validate_repo_contracts.py --mode test
	$(PYTHON) -m unittest discover -s tests -p test_scirhc_doctrine.py
	$(PYTHON) scripts/python_importer_conformance.py --mode test
	$(PYTHON) scripts/rust_importer_conformance.py --mode test
	$(PYTHON) scripts/scir_bootstrap_pipeline.py --mode test

validate:
	$(PYTHON) scripts/run_repo_validation.py

benchmark:
	$(PYTHON) scripts/benchmark_contract_dry_run.py --output-dir artifacts/benchmark_runs/latest

benchmark-claim:
	$(PYTHON) scripts/benchmark_contract_dry_run.py --claim-run --output-dir artifacts/benchmark_runs/claim

benchmark-repro:
	$(PYTHON) scripts/benchmark_repro.py --run-id $(RUN_ID)

ci: build lint test validate benchmark
