"""Generate/review explicit-state Simulink parity fixtures using the CFDC reference.

Run from the repository root with uv run --locked python simulations/tests/reference_parity.py.
This verification utility is not used by the MATLAB apparatus.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from cfdc.kernel.controllers import ControllerIR
from cfdc.sim.execution import LinearPlant, simulate_trial


def prepare(folder: Path) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    cases = sorted((ROOT / "simulations").glob("0*/case_config.json"))
    fixtures = []
    for path in cases:
        config = json.loads(path.read_text())
        task, plant = config["task"], config["plant"]
        u, y = task["control_input"], task["measured_signals"][0]
        sign = np.sign(plant["numerator"][0])
        family = {"optical": "PI", "vacuum": "delay_aware_PI", "ink": "two_dof_PI"}[
            plant["kind"]
        ]
        params = {
            "kp": float(sign * 2),
            "ki": float(sign),
            "reference_filter_rate": 2.0,
        }
        if family == "two_dof_PI":
            params["feedforward_gain"] = -0.5
        ir = ControllerIR(
            family,
            (y,),
            (u,),
            params,
            {key: (-20.0, 20.0) for key in params},
            integral_handling="anti_windup",
        ).to_dict()
        request = {
            "controller": ir,
            "sample_time_s": 0.02,
            "horizon_s": 20.0,
            "tracked_signals": [y],
            "measured_signals": [y],
            "control_inputs": [u],
            "references": {y: task["reference"]},
            "input_bounds": {u: [-1.0, 1.0]},
            "state_stop": 3.0,
            "output_bounds": {},
            "state_bounds": {},
            "controller_state_bounds": {},
            "phases": [],
            "disturbance": None,
        }
        if config["case_id"].startswith("04"):
            request["phases"] = [
                {
                    "phase_id": f"phase_{i}",
                    "references": {y: ref},
                    "exit_predicate": {
                        "kind": "within_band",
                        "signal": y,
                        "target": ref,
                        "tolerance": 0.03,
                    },
                    "dwell_s": 0.2,
                    "timeout_s": 20.0,
                    "hysteresis": 0.01,
                    "state_policy": "inherit",
                }
                for i, ref in enumerate([0.25, 0.5, 0.5])
            ]
        if config["case_id"].startswith("05"):
            request["disturbance"] = {
                "channel": u,
                "time_s": 2.0,
                "duration_s": 1.0,
                "amplitude": 0.1,
            }
        variants = {"nominal": request}
        if plant["kind"] == "optical":
            saturated = copy.deepcopy(request)
            saturated["input_bounds"][u] = [-0.1, 0.1]
            saturated["state_stop"] = 0.05
            variants["saturation_stop"] = saturated
        if config["case_id"].startswith("04"):
            reset = copy.deepcopy(request)
            reset["phases"][1]["state_policy"] = "reset"
            variants["reset_handoff"] = reset
            timeout = copy.deepcopy(request)
            timeout["phases"][0]["timeout_s"] = 0.1
            variants["phase_timeout"] = timeout
        if config["case_id"].startswith("05"):
            fractional = copy.deepcopy(request)
            fractional["disturbance"]["time_s"] = 2.007
            fractional["disturbance"]["duration_s"] = 1.006
            variants["fractional_disturbance"] = fractional
        for variant, req in variants.items():
            x0 = np.linspace(-0.8e-6, 0.6e-6, len(plant["denominator"]) - 1)
            reference_plant = LinearPlant.from_transfer_matrix(
                [[(plant["numerator"], plant["denominator"])]],
                inputs=(u,),
                outputs=(y,),
                delays={u: plant["input_delay_s"]},
            )
            reference_plant._state = x0.copy()
            scenario = {
                "trial_id": variant,
                "scenario_id": config["case_id"],
                "seed": 123,
            }
            expected = simulate_trial(req, scenario, reference_plant)
            name = config["case_id"] + "_" + variant
            item = {
                "name": name,
                "case_dir": str(path.parent),
                "initial_state": x0.tolist(),
                "request": req,
                "scenario": scenario,
            }
            fixtures.append(item)
            (folder / (name + "_expected.json")).write_text(json.dumps(expected))
    (folder / "fixtures.json").write_text(json.dumps(fixtures, indent=2))
    print(f"Prepared {len(fixtures)} explicit-state parity fixtures in {folder}")


def compare(expected, actual, path=""):
    if isinstance(expected, dict):
        assert set(expected) == set(actual), (path, set(expected), set(actual))
        for key, value in expected.items():
            compare(value, actual[key], path + "." + key)
    elif isinstance(expected, list):
        assert isinstance(actual, list) and len(expected) == len(actual), (
            path,
            len(expected),
            type(actual),
        )
        for i, (left, right) in enumerate(zip(expected, actual, strict=True)):
            compare(left, right, f"{path}[{i}]")
    elif isinstance(expected, (int, float)) and not isinstance(expected, bool):
        assert np.isclose(expected, actual, atol=1e-10, rtol=1e-8), (
            path,
            expected,
            actual,
        )
    else:
        assert expected == actual, (path, expected, actual)


def check(folder: Path):
    fixtures = json.loads((folder / "fixtures.json").read_text())
    for fixture in fixtures:
        name = fixture["name"]
        compare(
            json.loads((folder / (name + "_expected.json")).read_text()),
            json.loads((folder / (name + "_actual.json")).read_text()),
        )
        print("PASS", name)
    print(
        f"{len(fixtures)} Simulink/reference trajectories, states, phases and events match."
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["prepare", "check"])
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    (prepare if args.mode == "prepare" else check)(args.directory)
