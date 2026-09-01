"""Development selection must never learn from fresh confirmation."""

from cfdc.kernel.tuning import TuningContract, run_bounded_tuning


def contract(**kwargs):
    return TuningContract(
        parameter_whitelist=("kp",),
        parameter_domains={"kp": (-10.0, 10.0)},
        max_probes=3,
        probe_multipliers=(0.5, 0.75, 1.25),
        budget_confirmed=True,
        **kwargs,
    )


def baseline(score=10.0):
    return {"stable": True, "performance_pass": False, "score": score}


def test_development_finishes_before_one_fresh_and_failure_ends_round():
    calls = []

    def evaluate(parameters, split, repeats):
        calls.append((split, parameters["kp"]))
        if split == "fresh":
            return {"stable": False, "performance_pass": False, "score": 1e12}
        return {
            "stable": True,
            "performance_pass": False,
            "score": {1.0: 8.0, 1.5: 5.0, 2.5: 7.0}[parameters["kp"]],
        }

    result = run_bounded_tuning(
        {"kp": 2.0}, contract(), evaluate, baseline_result=baseline()
    )
    assert calls == [
        ("development", 1.0),
        ("development", 1.5),
        ("development", 2.5),
        ("fresh", 1.5),
    ]
    assert result.status == "confirmation_failed"
    assert result.accepted is False
    assert result.best_parameters == {"kp": 1.5}


def test_identical_zero_score_never_counts_as_improvement_or_calls_fresh():
    calls = []

    def evaluate(parameters, split, repeats):
        calls.append(split)
        return baseline(0.0)

    result = run_bounded_tuning(
        {"kp": 2.0},
        contract(minimum_relative_improvement=0.0),
        evaluate,
        baseline_result=baseline(0.0),
    )
    assert not result.accepted
    assert result.best_parameters == {"kp": 2.0}
    assert calls == ["development"] * 3


def test_relative_and_strict_improvement_both_required():
    calls = []

    def evaluate(parameters, split, repeats):
        calls.append(split)
        return baseline(9.9)

    result = run_bounded_tuning(
        {"kp": 2.0}, contract(), evaluate, baseline_result=baseline()
    )
    assert not result.accepted
    assert "fresh" not in calls


def test_safe_improving_nonpassing_candidate_is_selected_without_using_fresh_score():
    def evaluate(parameters, split, repeats):
        if split == "fresh":
            return {"stable": True, "performance_pass": True, "score": 0.01}
        return baseline({1.0: 8.0, 1.5: 5.0, 2.5: 7.0}[parameters["kp"]])

    result = run_bounded_tuning(
        {"kp": 2.0}, contract(), evaluate, baseline_result=baseline()
    )
    assert result.accepted
    assert result.best_parameters == {"kp": 1.5}
    assert result.best_score == 5.0
    assert result.probes[-1]["fresh"]["score"] == 0.01


def test_negative_direction_gain_candidates_preserve_signed_domain():
    calls = []

    def evaluate(parameters, split, repeats):
        calls.append((split, parameters["kp"]))
        return {"stable": True, "performance_pass": True, "score": 0.0}

    result = run_bounded_tuning(
        {"kp": -2.0}, contract(), evaluate, baseline_result=baseline()
    )
    assert [gain for split, gain in calls if split == "development"] == [
        -1.0,
        -1.5,
        -2.5,
    ]
    assert result.accepted
