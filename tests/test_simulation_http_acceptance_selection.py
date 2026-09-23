"""Selected simulation acceptance jobs stay portable between Docker and MATLAB."""

import json
import shutil
from pathlib import Path

from simulations.tests import http_acceptance

ROOT = Path(__file__).resolve().parents[1]
SELECTED = ("02_vacuum_hold", "05_ink_disturbance_recovery")


def test_selected_cases_emit_only_portable_exchange_jobs(tmp_path: Path) -> None:
    case_root = tmp_path / "simulations"
    for case_id in SELECTED:
        source = ROOT / "simulations" / case_id / "case_config.json"
        target = case_root / case_id / "case_config.json"
        target.parent.mkdir(parents=True)
        shutil.copyfile(source, target)

    folder = tmp_path / "http"
    http_acceptance.run("init", folder, cases=SELECTED, case_root=case_root)

    state = json.loads((folder / "state.json").read_text(encoding="utf-8"))
    assert {item["case_id"] for item in state["cases"]} == set(SELECTED)
    assert len(state["cases"]) == 2
    exchange = json.loads((folder / "jobs-exchange.json").read_text(encoding="utf-8"))
    assert len(exchange) == 2
    for job in exchange:
        for key in ("case_dir", "package_path", "response_path"):
            assert not Path(job[key]).is_absolute()
        assert (tmp_path / job["case_dir"] / "case_config.json").is_file()
        assert (tmp_path / job["package_path"]).is_file()
        assert Path(job["response_path"]).parent == Path("http")
