from __future__ import annotations

import sys
import unittest
from dataclasses import replace
from pathlib import Path


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
    scirh_to_scirhc,
)
from scir_bootstrap_pipeline import (  # noqa: E402
    generate_scirhc_report_artifact,
    make_scirhc_generation_context,
)
from scir_h_bootstrap_model import (  # noqa: E402
    CompressionOrigin,
    FunctionDecl,
    HcFunctionDecl,
    Module,
    NameExpr,
    Param,
    ReturnStmt,
    ScirhcContextError,
    VarDecl,
    scirh_to_scirhc as public_scirh_to_scirhc,
)
from validators.execution_context_guard import (  # noqa: E402
    ScirhcExecutionCapability,
    ScirhcExecutionProvenance,
    TrustedScirhcCaller,
)
from validators.scirhc_validator import (  # noqa: E402
    ScirHcDoctrineError,
    assert_claim_scope_compliance,
    assert_deterministic_derivation,
    assert_lineage_integrity,
)


def sample_module() -> Module:
    return Module(
        module_id="fixture.test.scirhc_adversarial",
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


def sample_claim_report(module: Module) -> dict:
    lineage_root = build_scirhc_lineage_root(module)
    lineage_references = {
        lineage_root.module_id: {
            "semantic_lineage_id": lineage_root.semantic_lineage_id,
            "normalized_canonical_hash": lineage_root.normalized_canonical_hash,
        }
    }
    return {
        "claim_class": "LEXICAL_COMPRESSION_ONLY",
        "evidence_class": ["scirhc_lcr_vs_ast"],
        "representation": "SCIR-Hc",
        "scir_h_lineage_references": lineage_references,
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
                    "scir_h_evidence": [module.module_id],
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
                "baseline_name": "typed-AST",
                "metric": "LCR_scirhc",
                "metric_class": "DESCRIPTIVE",
                "scir_h_evidence": [module.module_id],
                "observed_value": 0.7,
                "baseline_value": 0.8,
                "delta": -0.1,
                "confidence_range": None,
            }
        ],
    }


class ScirHcAdversarialTests(unittest.TestCase):
    def test_direct_transform_invocation_attack_fails(self) -> None:
        module = sample_module()
        with self.assertRaisesRegex(ScirhcContextError, "Missing SCIR-Hc generation context|Unauthorized SCIR-Hc transform access"):
            scirh_to_scirhc(module)
        with self.assertRaisesRegex(ScirhcContextError, "Unauthorized SCIR-Hc transform access"):
            public_scirh_to_scirhc(module)

    def test_forged_context_attack_fails(self) -> None:
        module = sample_module()
        valid_ctx = make_scirhc_generation_context(module, report_context="validation_report")
        fake_capability = ScirhcExecutionCapability(
            caller=TrustedScirhcCaller.BENCHMARK_CLAIM,
            nonce=object(),
        )
        forged_ctx = ScirhcGenerationContext(
            report_surface=valid_ctx.report_surface,
            generation_token=build_scirhc_generation_token(valid_ctx.lineage_root, valid_ctx.provenance),
            lineage_root=valid_ctx.lineage_root,
            provenance=ScirhcExecutionProvenance(TrustedScirhcCaller.BENCHMARK_CLAIM),
            capability=fake_capability,
        )
        with self.assertRaisesRegex(ScirhcContextError, "Untrusted SCIR-Hc execution capability|Unauthorized"):
            generate_scirhc_report_artifact(module, ctx=forged_ctx)

    def test_partial_lineage_injection_fails(self) -> None:
        module = sample_module()
        report = sample_claim_report(module)
        report["scir_h_lineage_references"] = {}
        with self.assertRaisesRegex(ScirHcDoctrineError, "missing lineage bindings|declare canonical SCIR-H lineage references"):
            assert_lineage_integrity(report, {module.module_id: module})

    def test_metric_authority_escalation_fails(self) -> None:
        module = sample_module()
        report = sample_claim_report(module)
        report["claim_gate"]["evaluated_conditions"][0]["metric"] = "semantic_authority_score"
        report["claim_gate"]["evaluated_conditions"][0]["statement"] = "Semantic authority score proves preservation."
        report["claim_gate"]["evaluated_conditions"][0]["metric_class"] = "DESCRIPTIVE"
        report["claims"][0]["metric"] = "semantic_authority_score"
        report["claims"][0]["statement"] = "Semantic authority score proves preservation."
        with self.assertRaisesRegex(ScirHcDoctrineError, "exceeds claim_class|implies semantic authority|derived-only evidence|not derived from the declared SCIR-H evidence scope"):
            assert_claim_scope_compliance(report, canonical_registry={module.module_id: module})

    def test_idempotence_violation_fails(self) -> None:
        module = sample_module()
        ctx = make_scirhc_generation_context(module, report_context="validation_report")
        hc_module, _, _, _, _ = generate_scirhc_report_artifact(module, ctx=ctx)
        drifted_hc = replace(
            hc_module,
            functions=(
                replace(
                    hc_module.functions[0],
                    return_type="opaque<ForeignResult>",
                    compression_origin=(CompressionOrigin.INFERRED_EFFECT,),
                ),
            ),
        )
        with self.assertRaisesRegex(ScirHcDoctrineError, "deterministic|Invalid|preserve|Non-idempotent"):
            assert_deterministic_derivation(module, drifted_hc)


if __name__ == "__main__":
    unittest.main()
