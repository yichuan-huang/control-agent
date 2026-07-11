import pytest

from cfdc.diagnosis import clarification_question_map, continue_diagnostic_session, start_diagnostic_session
from cfdc.diagnosis.engine import infer_structural_diagnosis
from cfdc.models import DiagnosticSessionState, SystemDescription


class SequencedAdapter:
    def __init__(self, payloads): self.payloads, self.index = list(payloads), 0
    def diagnose(self, description):
        payload = self.payloads[min(self.index, len(self.payloads)-1)]; self.index += 1; return payload


def _incomplete(): return infer_structural_diagnosis(SystemDescription(text="I have a machine.")).model_dump()
def _complete(): return infer_structural_diagnosis(SystemDescription(text="A first order temperature process settles after a heater change.", observed_outputs=["temperature"], actuators=["heater"])).model_dump()


def test_session_round_trip_and_stable_question_ids():
    adapter = SequencedAdapter([_incomplete(), _complete()])
    state = start_diagnostic_session(SystemDescription(text="I have a machine."), diagnostic_adapter=adapter)
    ids = clarification_question_map(state)
    assert state.status == "collecting_information"
    assert all(key.startswith("q_") for key in ids)
    assert DiagnosticSessionState.model_validate_json(state.model_dump_json()) == state
    completed = continue_diagnostic_session(state, {next(iter(ids)): "It settles and I can record it."}, supplemental_description="A heater changes measured temperature.", diagnostic_adapter=adapter)
    assert completed.status == "ready_for_experiments"
    assert completed.semantic_selection is not None
    assert completed.compiled_route.executable


def test_session_accepts_supplemental_description_without_keyed_answers():
    adapter = SequencedAdapter([_incomplete(), _complete()])
    state = start_diagnostic_session(SystemDescription(text="I have a machine."), diagnostic_adapter=adapter)
    completed = continue_diagnostic_session(state, supplemental_description="It is a measured first-order thermal loop with a heater.", diagnostic_adapter=adapter)
    assert completed.current_diagnosis.complete


def test_session_rejects_unknown_question_id():
    state = start_diagnostic_session(SystemDescription(text="I have a machine."), diagnostic_adapter=SequencedAdapter([_incomplete()]))
    with pytest.raises(ValueError, match="unknown clarification"):
        continue_diagnostic_session(state, {"q_invalid": "answer"}, diagnostic_adapter=SequencedAdapter([_complete()]))
