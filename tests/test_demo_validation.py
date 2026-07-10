from cfdc.demo import run_demo_validation


def test_stable_demo_validation_passes_and_is_deterministic():
    first = run_demo_validation()
    second = run_demo_validation()

    assert first == second
    assert first["passed"] is True
    assert first["passed_count"] == 4
    assert [result["route_id"] for result in first["results"]] == [
        "cartpole",
        "vtol-position",
        "vtol-boundary",
        "vtol-variation",
    ]
    assert all(result["performance"]["success"] for result in first["results"])
    assert all("final_error" in result["performance"] for result in first["results"])
