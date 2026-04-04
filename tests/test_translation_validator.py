from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
FIXTURES_DIR = ROOT / "tests" / "fixtures" / "translation_validation"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from runtime.scirl_interpreter import HostFunctionSpec  # noqa: E402
from scir_bootstrap_pipeline import (  # noqa: E402
    emit_wasm_module,
    lower_rust_supported_module,
    lower_supported_module,
)
from scir_python_bootstrap import SCIRH_MODULES as PYTHON_SCIRH_MODULES  # noqa: E402
from scir_rust_bootstrap import SCIRH_MODULES as RUST_SCIRH_MODULES  # noqa: E402
from validators.translation_validator import (  # noqa: E402
    build_provenance_index,
    compare_observations,
    validate_translation,
)


def wasm_artifact(module, wat_text: str) -> dict:
    return {
        "kind": "wasm",
        "subject": module.module_id,
        "module_id": module.module_id,
        "text": wat_text,
        "source_module": module,
        "preservation_contract": {
            "preservation_level": "P2",
            "allowed_allocation_variation": True,
            "allowed_scheduling_variation": False,
            "fp_tolerance": 0.0,
        },
    }


def opaque_python_artifact(module, *, rogue_capability: bool = False, missing_effect: bool = False) -> dict:
    host_spec = HostFunctionSpec(
        handler=lambda: {"status": "ok"},
        capabilities=("capability:foreign_api_ping",),
    )
    artifact = {
        "kind": "python",
        "subject": module.module_id,
        "module_id": module.module_id,
        "source_text": "import foreign_api\n\n\ndef ping():\n    return foreign_api.ping()\n",
        "filename": "<translation-python-opaque>",
        "source_module": module,
        "host_functions": {
            "foreign_api_ping": HostFunctionSpec(
                handler=lambda: {"status": "ok"},
                capabilities=("capability:foreign_api_ping",) if not missing_effect else (),
            )
        },
        "host_modules": {
            "foreign_api": {
                "ping": HostFunctionSpec(
                    handler=lambda: {"status": "ok"},
                    capabilities=("capability:rogue",) if rogue_capability else ("capability:foreign_api_ping",),
                )
                if not missing_effect
                else (lambda: {"status": "ok"})
            }
        },
        "boundary_contracts": {
            "boundary_id": "fixture.python_importer.c_opaque_call.boundary.foreign_api_ping",
            "kind": "opaque_call",
            "capabilities": ["capability:foreign_api_ping"],
        },
        "preservation_contract": {
            "preservation_level": "P3",
            "allowed_allocation_variation": False,
            "allowed_scheduling_variation": False,
            "fp_tolerance": 0.0,
        },
    }
    if not rogue_capability and not missing_effect:
        artifact["host_modules"]["foreign_api"]["ping"] = host_spec
        artifact["host_functions"]["foreign_api_ping"] = host_spec
    return artifact


def comparison_contract(
    equivalence_mode: str,
    observable_dimensions: list[str],
    *,
    allow_contract_bounded: bool = False,
    preservation_level: str = "P1",
) -> dict:
    return {
        "equivalence_mode": equivalence_mode,
        "observable_dimensions_checked": observable_dimensions,
        "allow_contract_bounded": allow_contract_bounded,
        "allowed_allocation_variation": allow_contract_bounded,
        "allowed_scheduling_variation": False,
        "fp_tolerance": 0.0,
        "preservation_level": preservation_level,
    }


class TranslationValidatorTests(unittest.TestCase):
    def test_translation_trace_match_reports_subset_strength(self) -> None:
        module = PYTHON_SCIRH_MODULES["a_basic_function"]
        lowered = lower_supported_module(module)
        wat_text, _ = emit_wasm_module(module, lowered)
        report = validate_translation(lowered, wasm_artifact(module, wat_text), "P")
        self.assertEqual(report["outcome"], "PASSED_SUBSET")
        self.assertEqual(report["validation_strength"], "execution_backed_subset")
        self.assertEqual(report["backend_subset_class"], "wasm_helper_free_bounded")
        self.assertEqual(report["subset_admission_result"], "admitted")
        self.assertEqual(report["equivalence_mode"], "contract_bounded")
        self.assertEqual(report["downgrade_reason"], "helper_free_subset_bounded_execution")
        self.assertTrue(report["helper_free_subset_required"])
        self.assertTrue(all(report["dimension_results"].values()))

    def test_unsupported_helper_usage_downgrades_deterministically(self) -> None:
        module = PYTHON_SCIRH_MODULES["b_direct_call"]
        lowered = lower_supported_module(module)
        wat_text = (FIXTURES_DIR / "unsupported_helper_module.wat").read_text(encoding="utf-8")
        report = validate_translation(lowered, wasm_artifact(module, wat_text), "P")
        self.assertEqual(report["outcome"], "DOWNGRADED_UNSUPPORTED_SUBSET")
        self.assertEqual(report["validation_strength"], "unsupported")
        self.assertEqual(report["validated_invocations"], 0)
        self.assertIn("imports_outside_allowed_shims", report["unsupported_features_detected"])
        self.assertIn("helper_usage_outside_admitted_subset", report["subset_admission_reason"])

    def test_effect_violation_detection(self) -> None:
        module = PYTHON_SCIRH_MODULES["c_opaque_call"]
        lowered = lower_supported_module(module)
        report = validate_translation(lowered, opaque_python_artifact(module, missing_effect=True), "D-PY")
        self.assertEqual(report["outcome"], "FAILED_MISMATCH")
        self.assertFalse(report["dimension_results"]["effect_trace"])
        self.assertTrue(any(finding["dimension"] == "effect_trace" for finding in report["findings"]))

    def test_capability_violation_reports_provenance(self) -> None:
        module = PYTHON_SCIRH_MODULES["c_opaque_call"]
        lowered = lower_supported_module(module)
        report = validate_translation(lowered, opaque_python_artifact(module, rogue_capability=True), "D-PY")
        self.assertEqual(report["outcome"], "FAILED_MISMATCH")
        self.assertFalse(report["dimension_results"]["capability_trace"])
        self.assertTrue(report["suspect_l_nodes"])
        self.assertTrue(report["suspect_h_nodes"])
        self.assertTrue(
            any(link["dimension"] == "capability_trace" for link in report["origin_trace_links"])
        )

    def test_contract_bounded_equivalence_for_record_cell_slice(self) -> None:
        module = RUST_SCIRH_MODULES["a_struct_field_borrow_mut"]
        lowered = lower_rust_supported_module(module)
        wat_text, _ = emit_wasm_module(module, lowered)
        report = validate_translation(lowered, wasm_artifact(module, wat_text), "P")
        self.assertEqual(report["outcome"], "PASSED_SUBSET")
        self.assertIn("record-cell ABI limited to the fixed offset=0 shared-handle slice", report["contract_assumptions"])

    def test_exact_sequential_trace_mode_rejects_contract_bounded_normalization(self) -> None:
        module = PYTHON_SCIRH_MODULES["a_basic_function"]
        lowered = lower_supported_module(module)
        wat_text, _ = emit_wasm_module(module, lowered)
        report = validate_translation(
            lowered,
            wasm_artifact(module, wat_text),
            "P",
            equivalence_mode="sequential_trace",
            observable_dimensions=[
                "returns",
                "traps_or_exceptions",
                "termination_kind",
                "branch_trace",
                "state_write_trace",
                "effect_trace",
            ],
            allow_contract_bounded=False,
        )
        self.assertEqual(report["outcome"], "FAILED_MISMATCH")
        self.assertFalse(report["dimension_results"]["state_write_trace"])
        self.assertFalse(report["dimension_results"]["effect_trace"])

    def test_adversarial_observation_corpus(self) -> None:
        fixtures = json.loads((FIXTURES_DIR / "adversarial_observations.json").read_text(encoding="utf-8"))
        provenance_modules = {
            "a_basic_function": lower_supported_module(PYTHON_SCIRH_MODULES["a_basic_function"]),
            "b_direct_call": lower_supported_module(PYTHON_SCIRH_MODULES["b_direct_call"]),
            "c_opaque_call": lower_supported_module(PYTHON_SCIRH_MODULES["c_opaque_call"]),
            "a_struct_field_borrow_mut": lower_rust_supported_module(RUST_SCIRH_MODULES["a_struct_field_borrow_mut"]),
        }
        for fixture in fixtures:
            with self.subTest(fixture=fixture["id"]):
                comparison = compare_observations(
                    fixture["oracle"],
                    fixture["backend"],
                    comparison_contract(
                        fixture["equivalence_mode"],
                        fixture["observable_dimensions"],
                    ),
                    declared_capabilities=set(fixture["declared_capabilities"]),
                    provenance_index=build_provenance_index(provenance_modules[fixture["provenance_case"]]),
                    invocation={"function": fixture["id"], "args": []},
                    backend_kind="wasm",
                )
                self.assertFalse(comparison["dimension_results"][fixture["expected_dimension"]])
                self.assertTrue(
                    any(finding["dimension"] == fixture["expected_dimension"] for finding in comparison["findings"])
                )


if __name__ == "__main__":
    unittest.main()
