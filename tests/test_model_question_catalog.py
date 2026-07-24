from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from cfdc.lab.model_contracts import (
    DiscoveryQuestion,
    ModelFactAnswer,
    ModelQuestionExample,
    ModelQuestionExampleCatalog,
)
from cfdc.lab.model_questions import (
    adopt_example_answer,
    load_model_question_examples,
)


def test_catalog_is_versioned_and_covers_required_fact_types():
    catalog = load_model_question_examples()

    assert catalog.schema_version == "model_question_examples/v1"
    assert {
        "input_step",
        "output_step",
        "response_delay",
        "response_time_63",
        "oscillation_period",
        "peak_ratio",
        "sample_time",
        "operating_point",
        "validity_region",
        "signal_definition",
        "state_space_data",
        "cartpole_parameters",
        "vtol_parameters",
    } <= {item.fact_type for item in catalog.examples}


def test_catalog_rows_are_fixed_chinese_examples_with_unique_ids():
    catalog = load_model_question_examples()

    assert len(catalog.examples) == len(
        {item.example_id for item in catalog.examples}
    )
    assert all(item.context_tags for item in catalog.examples)
    assert all(item.answer_text for item in catalog.examples)
    assert all(item.value_payload for item in catalog.examples)
    assert any("\u4e00" <= character <= "\u9fff" for character in catalog.examples[0].answer_text)


def test_adoption_records_exact_version_hash_and_source():
    catalog = load_model_question_examples()
    question = DiscoveryQuestion(
        question_id="q-input-step",
        fact_id="input_step",
        fact_type="input_step",
        prompt="你把加热功率从多少调到多少？",
        answer_kind="text",
        unit_family="power",
        example_id="thermal.input_step.power.v1",
        why_needed="用于计算输入变化量。",
    )

    answer = adopt_example_answer(
        question, catalog, adopted_at="2026-07-23T12:00:00+00:00"
    )

    assert answer.source == "user_adopted_example"
    assert answer.example_catalog_version == catalog.catalog_version
    assert len(answer.example_content_sha256 or "") == 64
    assert answer.adopted_at == "2026-07-23T12:00:00+00:00"


def test_adoption_rejects_unknown_or_mismatched_example():
    catalog = load_model_question_examples()
    unknown = DiscoveryQuestion(
        question_id="q-unknown",
        fact_id="input_step",
        fact_type="input_step",
        prompt="输入如何变化？",
        answer_kind="text",
        unit_family="power",
        example_id="unknown.example.v1",
        why_needed="用于建模。",
    )
    mismatched = unknown.model_copy(
        update={"example_id": "thermal.input_step.power.v1", "fact_type": "sample_time"}
    )

    with pytest.raises(ValueError, match="unknown example"):
        adopt_example_answer(
            unknown, catalog, adopted_at="2026-07-23T12:00:00+00:00"
        )
    with pytest.raises(ValueError, match="does not match"):
        adopt_example_answer(
            mismatched, catalog, adopted_at="2026-07-23T12:00:00+00:00"
        )


def test_catalog_rejects_version_or_content_hash_mismatch():
    catalog = load_model_question_examples()
    payload = catalog.model_dump(mode="json")

    with pytest.raises(ValueError, match="version"):
        ModelQuestionExampleCatalog.model_validate(
            {**payload, "catalog_version": "v2"}
        )
    with pytest.raises(ValueError, match="hash"):
        ModelQuestionExampleCatalog.model_validate(
            {**payload, "content_sha256": "0" * 64}
        )


def test_packaged_catalog_json_is_canonical_and_hash_checked():
    catalog = load_model_question_examples()
    payload = json.loads(
        (
            __import__("pathlib").Path(__file__).parents[1]
            / "cfdc"
            / "lab"
            / "resources"
            / "model_question_examples.v1.json"
        ).read_text(encoding="utf-8")
    )

    assert ModelQuestionExampleCatalog.model_validate(payload) == catalog


def _example_payload(**updates):
    payload = {
        "example_id": "test.input_step.power.v1",
        "fact_type": "input_step",
        "unit_family": "power",
        "context_tags": ["test"],
        "answer_text": "把功率从 10 W 调到 20 W。",
        "value_payload": {"before": 10.0, "after": 20.0, "unit": "W"},
    }
    payload.update(updates)
    return payload


_MISSING = object()


@pytest.mark.parametrize(
    ("contract", "fact_type"),
    [
        (ModelQuestionExample, _MISSING),
        (ModelQuestionExample, None),
        (ModelFactAnswer, _MISSING),
        (ModelFactAnswer, None),
    ],
)
def test_fact_payload_validation_never_leaks_key_error(
    contract,
    fact_type,
):
    if contract is ModelQuestionExample:
        payload = _example_payload()
    else:
        payload = {
            "fact_id": "input_step",
            "fact_type": "input_step",
            "answer_text": "把功率从 10 W 调到 20 W。",
            "value_payload": {
                "before": 10.0,
                "after": 20.0,
                "unit": "W",
            },
            "unit_family": "power",
            "source": "user_supplied",
        }
    if fact_type is _MISSING:
        payload.pop("fact_type")
    else:
        payload["fact_type"] = fact_type

    with pytest.raises(ValidationError):
        contract.model_validate(payload)


@pytest.mark.parametrize(
    "forbidden_key",
    [
        "code",
        "ode",
        "callback",
        "url",
        "module",
        "path",
        "expression",
        "function",
        "api_key",
        "token",
        "secret",
        "password",
    ],
)
def test_fact_payloads_reject_recursive_forbidden_and_sensitive_keys(
    forbidden_key,
):
    value_payload = {
        "before": 10.0,
        "after": 20.0,
        "unit": "W",
        "metadata": {"nested": {forbidden_key: "unsafe"}},
    }

    with pytest.raises(ValueError, match="forbidden"):
        ModelQuestionExample.model_validate(
            _example_payload(value_payload=value_payload)
        )
    with pytest.raises(ValueError, match="forbidden"):
        ModelFactAnswer(
            fact_id="input_step",
            fact_type="input_step",
            answer_text="把功率从 10 W 调到 20 W。",
            value_payload=value_payload,
            unit_family="power",
            source="user_supplied",
        )


@pytest.mark.parametrize("placeholder", ["unspecified", "unknown", "待定"])
def test_fact_payloads_reject_nested_placeholder_unit_values(placeholder):
    payload = {
        "inputs": [{"signal_id": "heater", "unit": "W"}],
        "outputs": [{"signal_id": "temperature", "unit": placeholder}],
    }

    with pytest.raises(ValueError, match="placeholder"):
        ModelQuestionExample.model_validate(
            _example_payload(
                fact_type="signal_definition",
                unit_family="signal",
                value_payload=payload,
            )
        )
    with pytest.raises(ValueError, match="placeholder"):
        ModelFactAnswer(
            fact_id="signals",
            fact_type="signal_definition",
            answer_text="输入是加热功率，输出是温度。",
            value_payload=payload,
            unit_family="signal",
            source="user_supplied",
        )


@pytest.mark.parametrize(
    "ranges",
    [
        {"valve": [50.0]},
        {"valve": [60.0, 40.0]},
        {"valve": ["low", 60.0]},
    ],
)
def test_validity_region_fact_payload_rejects_malformed_ranges(ranges):
    payload = {
        "input_ranges": ranges,
        "output_ranges": {"flow": [9.0, 15.0]},
        "signal_units": {"valve": "%", "flow": "L/min"},
    }

    with pytest.raises(ValueError, match="range"):
        ModelQuestionExample.model_validate(
            _example_payload(
                fact_type="validity_region",
                unit_family="operating_region",
                value_payload=payload,
            )
        )
