from __future__ import annotations

import json
import sys
import unittest
from dataclasses import replace
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from _internal.scirhc_transform import (  # noqa: E402
    ScirhcGenerationContext,
    build_scirhc_generation_token,
    build_scirhc_lineage_root,
    scirhc_lineage_root_payload,
    scirh_to_scirhc,
)
from scir_bootstrap_pipeline import (  # noqa: E402
    ForbiddenPathError,
    PipelineViolationError,
    emit_wasm_module,
    generate_scirhc_report_artifact,
    lower_supported_module,
    make_scirhc_generation_context,
    reconstruct_python_source,
)
from scir_h_bootstrap_model import (  # noqa: E402
    FunctionDecl,
    Module,
    NameExpr,
    Param,
    ReturnStmt,
    ScirhcContextError,
    VarDecl,
    scirh_to_scirhc as public_scirh_to_scirhc,
)
from scir_python_bootstrap import SCIRH_MODULES as PYTHON_SCIRH_MODULES  # noqa: E402
from validate_repo_contracts import collect_instance_validation_errors  # noqa: E402
from validators.scirhc_validator import (  # noqa: E402
    ScirHcDoctrineError,
    assert_claim_scope_compliance,
    assert_lineage_integrity,
    assert_metric_authority,
    assert_round_trip_integrity,
)
from validators.execution_context_guard import (  # noqa: E402
    ScirhcExecutionProvenance,
    TrustedScirhcCaller,
    register_trusted_scirhc_caller,
)


TEST_CAPABILITY = register_trusted_scirhc_caller(TrustedScirhcCaller.BENCHMARK_CLAIM)


def sample_module() -> Module:
    return Module(
        module_id="fixture.test.scirhc_doctrine",
        imports=(),
        type_decls=(),
        functions=(
            FunctionDecl(
                name="identity",
                params=(Param("x", "int"),),
                return_type="int",
                effects=(),
                body=(
                    VarDecl("y", "int", NameExpr("x")),
                    ReturnStmt(NameExpr("y")),
                ),
            ),
        ),
    )


def sample_lineage_references(module: Module) -> dict[str, dict[str, str]]:
    lineage_root = build_scirhc_lineage_root(module)
    return {
        lineage_root.module_id: scirhc_lineage_root_payload(lineage_root),
    }


def sample_claim_report() -> dict:
    module = sample_module()
    module_id = module.module_id
    return {
        "claim_class": "LEXICAL_COMPRESSION_ONLY",
        "evidence_class": ["scirhc_lcr_vs_ast"],
        "representation": "SCIR-Hc",
        "scir_h_lineage_references": sample_lineage_references(module),
        "claim_gate": {
            "passed": True,
            "ai_thesis_status": "supported",
            "satisfied_conditions": ["scirhc_lcr_vs_ast"],
            "evaluated_conditions": [
                {
                    "id": "scirhc_lcr_vs_ast",
                    "statement": "SCIR-Hc beats typed-AST on LCR.",
                    "baseline_name": "typed-AST",
                    "metric": "LCR_scirhc",
                    "metric_class": "DESCRIPTIVE",
                    "scir_h_evidence": [module_id],
                    "observed_value": 0.7,
                    "baseline_value": 0.8,
                    "delta": -0.1,
                    "threshold": 0.0,
                    "comparison": "lt",
                    "passed": True,
                }
            ],
        },
        "claims": [
            {
                "statement": "SCIR-Hc beats typed-AST on LCR.",
                "corpus_manifest": "reports/examples/corpus_manifest.example.json",
                "corpus_manifest_hash": "sha256:1111111111111111111111111111111111111111111111111111111111111111",
                "baseline_name": "typed-AST",
                "metric": "LCR_scirhc",
                "metric_class": "DESCRIPTIVE",
                "scir_h_evidence": [module_id],
                "observed_value": 0.7,
                "baseline_value": 0.8,
                "delta": -0.1,
                "confidence_range": None,
            }
        ],
    }


def benchmark_report_schema_errors(payload: dict) -> list[tuple[str, str]]:
    schema = json.loads((ROOT / "schemas" / "benchmark_report.schema.json").read_text(encoding="utf-8"))
    return list(collect_instance_validation_errors(payload, schema))


class ScirHcDoctrineTests(unittest.TestCase):
    def test_scirhc_generation_without_context_fails(self) -> None:
        with self.assertRaisesRegex(ScirhcContextError, "Missing SCIR-Hc generation context"):
            scirh_to_scirhc(sample_module())

    def test_scirhc_generation_outside_report_context_fails(self) -> None:
        lineage_root = build_scirhc_lineage_root(sample_module())
        ctx = ScirhcGenerationContext(
            report_surface="lowering_pass",
            generation_token=build_scirhc_generation_token(
                lineage_root,
                ScirhcExecutionProvenance(TEST_CAPABILITY.caller),
            ),
            lineage_root=lineage_root,
            provenance=ScirhcExecutionProvenance(TEST_CAPABILITY.caller),
            capability=TEST_CAPABILITY,
        )
        with self.assertRaisesRegex(ScirhcContextError, "Invalid SCIR-Hc report surface"):
            generate_scirhc_report_artifact(sample_module(), ctx=ctx)

    def test_invalid_lineage_hash_fails(self) -> None:
        report = sample_claim_report()
        module_id = sample_module().module_id
        report["scir_h_lineage_references"][module_id]["normalized_canonical_hash"] = "0" * 64
        with self.assertRaisesRegex(ScirHcDoctrineError, "Lineage hash mismatch"):
            assert_lineage_integrity(report, {module_id: sample_module()})

    def test_missing_lineage_coverage_fails(self) -> None:
        report = sample_claim_report()
        report["claims"][0]["scir_h_evidence"] = []
        with self.assertRaisesRegex(ScirHcDoctrineError, "Incomplete lineage coverage"):
            assert_lineage_integrity(report, {sample_module().module_id: sample_module()})

    def test_causal_metric_without_evidence_fails(self) -> None:
        claim_gate = {
            "evaluated_conditions": [
                {
                    "metric": "LCR_scirhc",
                    "metric_class": "DESCRIPTIVE",
                    "scir_h_evidence": [sample_module().module_id],
                }
            ]
        }
        with self.assertRaisesRegex(ScirHcDoctrineError, "Causal metric outside evaluated conditions"):
            assert_metric_authority(
                [
                    {
                        "metric": "causal_semantic_shift_score",
                        "metric_class": "CAUSAL",
                        "scir_h_evidence": [],
                        "statement": "Causal estimate.",
                    }
                ],
                claim_gate,
            )

    def test_metric_implying_authority_fails(self) -> None:
        claim_gate = {
            "evaluated_conditions": [
                {
                    "metric": "semantic_authority_score",
                    "metric_class": "DESCRIPTIVE",
                    "scir_h_evidence": [sample_module().module_id],
                }
            ]
        }
        with self.assertRaisesRegex(ScirHcDoctrineError, "Metric implies semantic authority"):
            assert_metric_authority(
                [
                    {
                        "metric": "semantic_authority_score",
                        "metric_class": "DESCRIPTIVE",
                        "scir_h_evidence": [sample_module().module_id],
                        "statement": "Semantic authority score.",
                    }
                ],
                claim_gate,
            )

    def test_round_trip_drift_fails(self) -> None:
        module = sample_module()
        drifted = replace(
            module,
            functions=(
                replace(
                    module.functions[0],
                    return_type="opaque<ForeignResult>",
                ),
            ),
        )
        with mock.patch("validators.scirhc_validator.scirhc_to_scirh", return_value=drifted):
            with self.assertRaisesRegex(ScirHcDoctrineError, "preserve|Non-idempotent"):
                assert_round_trip_integrity(module)

    def test_direct_public_transform_import_fails(self) -> None:
        with self.assertRaisesRegex(ScirhcContextError, "Unauthorized SCIR-Hc transform access"):
            public_scirh_to_scirhc(sample_module())

    def test_rejects_illegal_pipeline_usage(self) -> None:
        module = PYTHON_SCIRH_MODULES["a_basic_function"]
        with self.assertRaises(ForbiddenPathError):
            lower_supported_module(module, input_representation="SCIR-Hc")
        with self.assertRaises(ForbiddenPathError):
            reconstruct_python_source(module, input_representation="SCIR-Hc")
        lowered = lower_supported_module(module)
        with self.assertRaises(ForbiddenPathError):
            emit_wasm_module(module, lowered, input_representation="SCIR-Hc")

    def test_schema_requires_metric_class(self) -> None:
        report = json.loads((ROOT / "reports" / "examples" / "benchmark_report.example.json").read_text(encoding="utf-8"))
        report["claim_gate"]["evaluated_conditions"][0].pop("metric_class")
        self.assertTrue(benchmark_report_schema_errors(report))

    def test_claim_scope_uses_lineage_and_metric_class(self) -> None:
        report = sample_claim_report()
        assert_claim_scope_compliance(report, canonical_registry={sample_module().module_id: sample_module()})

    def test_pipeline_context_builder_accepts_report_surface(self) -> None:
        ctx = make_scirhc_generation_context(sample_module(), report_context="validation_report")
        self.assertTrue(ctx.is_report_context)

    def test_pipeline_context_builder_rejects_non_report_surface(self) -> None:
        with self.assertRaises(PipelineViolationError):
            make_scirhc_generation_context(sample_module(), report_context="lowering_pass")


if __name__ == "__main__":
    unittest.main()
