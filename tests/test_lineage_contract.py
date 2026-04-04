from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from scir_h_bootstrap_model import FunctionDecl, Module, NameExpr, Param, ReturnStmt, VarDecl  # noqa: E402
from validators.lineage_contract import (  # noqa: E402
    LineageContractError,
    assert_complete_lineage_binding,
    assert_report_lineage_binding,
    canonical_lineage_binding,
)


def sample_module(module_id: str = "fixture.test.lineage") -> Module:
    return Module(
        module_id=module_id,
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


class LineageContractTests(unittest.TestCase):
    def test_canonical_lineage_binding_uses_normalized_hash_and_lineage(self) -> None:
        binding = canonical_lineage_binding(sample_module())
        self.assertEqual(set(binding), {"semantic_lineage_id", "normalized_canonical_hash"})
        self.assertEqual(len(binding["semantic_lineage_id"]), 64)
        self.assertEqual(len(binding["normalized_canonical_hash"]), 64)

    def test_partial_binding_fails(self) -> None:
        module = sample_module()
        with self.assertRaisesRegex(LineageContractError, "missing lineage bindings|declare canonical SCIR-H lineage references"):
            assert_complete_lineage_binding(
                {},
                canonical_registry={module.module_id: module},
                required_modules={module.module_id},
                label="SCIR-Hc artifact",
            )

    def test_hash_mismatch_fails(self) -> None:
        module = sample_module()
        bad_binding = canonical_lineage_binding(module)
        bad_binding["normalized_canonical_hash"] = "0" * 64
        with self.assertRaisesRegex(LineageContractError, "Lineage hash mismatch"):
            assert_complete_lineage_binding(
                {module.module_id: bad_binding},
                canonical_registry={module.module_id: module},
                required_modules={module.module_id},
                label="SCIR-Hc artifact",
            )

    def test_report_evidence_must_be_fully_covered(self) -> None:
        module = sample_module()
        report = {
            "scir_h_lineage_references": {
                module.module_id: canonical_lineage_binding(module),
            },
            "claim_gate": {
                "evaluated_conditions": [
                    {
                        "metric": "LCR_scirhc",
                        "scir_h_evidence": ["fixture.test.unknown"],
                    }
                ]
            },
            "claims": [],
        }
        with self.assertRaisesRegex(LineageContractError, "Incomplete lineage coverage"):
            assert_report_lineage_binding(
                report,
                canonical_registry={module.module_id: module},
                required_modules={module.module_id},
            )


if __name__ == "__main__":
    unittest.main()
