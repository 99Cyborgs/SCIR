from __future__ import annotations

import sys
import unittest
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from scir_bootstrap_pipeline import lower_supported_module  # noqa: E402
from scir_python_bootstrap import SCIRH_MODULES as PYTHON_SCIRH_MODULES  # noqa: E402
from validators.translation_validator import build_provenance_index, compare_observations  # noqa: E402


def comparison_contract(
    observable_dimensions: list[str],
    *,
    equivalence_mode: str = "sequential_trace",
    allow_contract_bounded: bool = False,
) -> dict:
    return {
        "equivalence_mode": equivalence_mode,
        "observable_dimensions_checked": observable_dimensions,
        "allow_contract_bounded": allow_contract_bounded,
        "allowed_allocation_variation": allow_contract_bounded,
        "allowed_scheduling_variation": False,
        "fp_tolerance": 0.0,
        "preservation_level": "P1",
    }


def base_observation() -> dict:
    return {
        "returns": 1,
        "traps_or_exceptions": None,
        "termination_kind": "return",
        "call_trace": [
            {
                "kind": "call",
                "target": "identity",
                "args": [1],
            }
        ],
        "branch_trace": [True],
        "state_write_trace": [
            {
                "target_kind": "cell",
                "value": 1,
            }
        ],
        "effect_trace": [
            {
                "effect": "write",
                "target_kind": "cell",
                "value": 1,
            }
        ],
        "capability_trace": [
            "capability:foreign_api_ping"
        ],
    }


class TranslationValidatorMutationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.provenance_index = build_provenance_index(
            lower_supported_module(PYTHON_SCIRH_MODULES["c_opaque_call"])
        )

    def assert_mutation_fails(self, mutated: dict, dimension: str, *, declared_capabilities=None) -> None:
        comparison = compare_observations(
            base_observation(),
            mutated,
            comparison_contract([dimension]),
            declared_capabilities=set(declared_capabilities or ["capability:foreign_api_ping"]),
            provenance_index=self.provenance_index,
            invocation={"function": "mutation", "args": []},
            backend_kind="python",
        )
        self.assertFalse(comparison["dimension_results"][dimension])
        self.assertTrue(any(finding["dimension"] == dimension for finding in comparison["findings"]))

    def test_branch_target_mutation_fails(self) -> None:
        mutated = deepcopy(base_observation())
        mutated["branch_trace"] = [False]
        self.assert_mutation_fails(mutated, "branch_trace")

    def test_returned_constant_mutation_fails(self) -> None:
        mutated = deepcopy(base_observation())
        mutated["returns"] = 0
        self.assert_mutation_fails(mutated, "returns")

    def test_state_write_value_mutation_fails(self) -> None:
        mutated = deepcopy(base_observation())
        mutated["state_write_trace"][0]["value"] = 0
        self.assert_mutation_fails(mutated, "state_write_trace")

    def test_state_write_ordering_mutation_fails(self) -> None:
        mutated = deepcopy(base_observation())
        mutated["state_write_trace"] = [
            {"target_kind": "cell", "value": 2},
            {"target_kind": "cell", "value": 1},
        ]
        comparison = compare_observations(
            {
                **base_observation(),
                "state_write_trace": [
                    {"target_kind": "cell", "value": 1},
                    {"target_kind": "cell", "value": 2},
                ],
            },
            mutated,
            comparison_contract(["state_write_trace"]),
            declared_capabilities={"capability:foreign_api_ping"},
            provenance_index=self.provenance_index,
            invocation={"function": "mutation", "args": []},
            backend_kind="python",
        )
        self.assertFalse(comparison["dimension_results"]["state_write_trace"])

    def test_capability_event_mutation_fails(self) -> None:
        mutated = deepcopy(base_observation())
        mutated["capability_trace"] = ["capability:rogue"]
        self.assert_mutation_fails(mutated, "capability_trace")

    def test_effect_event_mutation_fails(self) -> None:
        mutated = deepcopy(base_observation())
        mutated["effect_trace"][0]["value"] = 0
        self.assert_mutation_fails(mutated, "effect_trace")

    def test_exception_versus_return_mutation_fails(self) -> None:
        mutated = deepcopy(base_observation())
        mutated["returns"] = None
        mutated["termination_kind"] = "trap"
        mutated["traps_or_exceptions"] = "RuntimeError: boom"
        self.assert_mutation_fails(mutated, "termination_kind")
        self.assert_mutation_fails(mutated, "traps_or_exceptions")

    def test_contract_bounded_normalization_is_explicit(self) -> None:
        oracle = deepcopy(base_observation())
        backend = deepcopy(base_observation())
        backend["state_write_trace"][0]["target_kind"] = "local"
        strict = compare_observations(
            oracle,
            backend,
            comparison_contract(["state_write_trace"], equivalence_mode="sequential_trace"),
            declared_capabilities={"capability:foreign_api_ping"},
            provenance_index=self.provenance_index,
            invocation={"function": "mutation", "args": []},
            backend_kind="wasm",
        )
        bounded = compare_observations(
            oracle,
            backend,
            comparison_contract(
                ["state_write_trace"],
                equivalence_mode="contract_bounded",
                allow_contract_bounded=True,
            ),
            declared_capabilities={"capability:foreign_api_ping"},
            provenance_index=self.provenance_index,
            invocation={"function": "mutation", "args": []},
            backend_kind="wasm",
        )
        self.assertFalse(strict["dimension_results"]["state_write_trace"])
        self.assertTrue(bounded["dimension_results"]["state_write_trace"])


if __name__ == "__main__":
    unittest.main()
