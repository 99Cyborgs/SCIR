from __future__ import annotations

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

from scir_bootstrap_pipeline import (  # noqa: E402
    ForbiddenPathError,
    emit_wasm_module,
    lower_supported_module,
    reconstruct_python_source,
)
from scir_h_bootstrap_model import (  # noqa: E402
    CompressionOrigin,
    FunctionDecl,
    Module,
    NameExpr,
    Param,
    ReturnStmt,
    VarDecl,
    scirh_to_scirhc,
)
from scir_python_bootstrap import SCIRH_MODULES as PYTHON_SCIRH_MODULES  # noqa: E402
from validators.scirhc_validator import (  # noqa: E402
    ScirHcDoctrineError,
    assert_claim_scope_compliance,
    assert_deterministic_derivation,
    assert_no_hidden_semantics,
    assert_not_semantic_authority,
    assert_round_trip_integrity,
)


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


class ScirHcDoctrineTests(unittest.TestCase):
    def test_rejects_non_deterministic_derivation(self) -> None:
        module = sample_module()
        scirhc = scirh_to_scirhc(module)
        function = scirhc.functions[0]
        mutated = replace(
            scirhc,
            functions=(
                replace(
                    function,
                    compression_origin=(
                        CompressionOrigin.OWNERSHIP_ELISION,
                        CompressionOrigin.INFERRED_EFFECT,
                    ),
                ),
            ),
        )
        with self.assertRaisesRegex(ScirHcDoctrineError, "deterministic"):
            assert_deterministic_derivation(module, mutated)

    def test_rejects_round_trip_equivalence_failure(self) -> None:
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
            with self.assertRaisesRegex(ScirHcDoctrineError, "preserve"):
                assert_round_trip_integrity(module)

    def test_rejects_illegal_pipeline_usage(self) -> None:
        module = PYTHON_SCIRH_MODULES["a_basic_function"]
        with self.assertRaises(ForbiddenPathError):
            lower_supported_module(module, input_representation="SCIR-Hc")
        with self.assertRaises(ForbiddenPathError):
            reconstruct_python_source(module, input_representation="SCIR-Hc")
        lowered = lower_supported_module(module)
        with self.assertRaises(ForbiddenPathError):
            emit_wasm_module(module, lowered, input_representation="SCIR-Hc")

    def test_rejects_hidden_semantic_injection(self) -> None:
        module = sample_module()
        scirhc = scirh_to_scirhc(module)
        function = scirhc.functions[0]
        first_stmt = function.body[0]
        mutated = replace(
            scirhc,
            functions=(
                replace(
                    function,
                    body=(replace(first_stmt, compression_origin=()), *function.body[1:]),
                ),
            ),
        )
        with self.assertRaisesRegex(ScirHcDoctrineError, "must explain type elision"):
            assert_no_hidden_semantics(mutated)

    def test_rejects_claim_overreach(self) -> None:
        report = {
            "claim_class": "LEXICAL_COMPRESSION_ONLY",
            "evidence_class": ["patch_composability_vs_ast"],
            "claim_gate": {
                "passed": True,
                "ai_thesis_status": "supported",
                "satisfied_conditions": ["patch_composability_vs_ast"],
                "evaluated_conditions": [
                    {
                        "id": "patch_composability_vs_ast",
                    }
                ],
            },
            "claims": [
                {
                    "statement": "SCIR-Hc proves semantic preservation.",
                    "metric": "patch_composability_gain_vs_typed_ast",
                }
            ],
        }
        with self.assertRaisesRegex(ScirHcDoctrineError, "cross-class|overreach"):
            assert_claim_scope_compliance(report)

    def test_rejects_semantic_authority_marker(self) -> None:
        scirhc = scirh_to_scirhc(sample_module())
        mutated = replace(scirhc, authority_boundary="CANONICAL_ONLY")
        with self.assertRaisesRegex(ScirHcDoctrineError, "authority boundary"):
            assert_not_semantic_authority(mutated)


if __name__ == "__main__":
    unittest.main()
