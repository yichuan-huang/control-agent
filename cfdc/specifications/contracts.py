"""Typed parameter templates consumed by the current Kernel."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class CFDCModel(BaseModel):
    """Base model that rejects undeclared fields for auditable JSON output."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True, allow_inf_nan=False)


class SpecificationFieldDefinition(CFDCModel):
    fact_id: str = Field(min_length=1)
    label: str = Field(min_length=1)
    canonical_unit: str = Field(min_length=1)
    accepted_units: list[str] = Field(min_length=1)
    unit_policy: Literal[
        "dimensioned",
        "open",
        "motion_acceleration",
        "actuator_per_input",
        "structured",
    ] = "dimensioned"
    prompt_template: str = Field(min_length=1)
    why_needed: str = Field(min_length=1)
    where_to_find: str = Field(min_length=1)
    example_template: str = Field(min_length=1)
    answer_kind: Literal["number", "matrix", "structured_model"] = "number"


class SpecificationCompletionPath(CFDCModel):
    path_id: str = Field(min_length=1)
    required_fact_ids: list[str] = Field(min_length=1)


class SpecificationTemplate(CFDCModel):
    template_id: str = Field(min_length=1)
    method_profile_id: str = Field(min_length=1)
    user_summary: str = Field(min_length=1)
    fields: list[SpecificationFieldDefinition] = Field(default_factory=list)
    completion_paths: list[SpecificationCompletionPath] = Field(min_length=1)
    compiler_id: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_completion_paths(self) -> SpecificationTemplate:
        known = {item.fact_id for item in self.fields}
        referenced = {
            fact_id
            for path in self.completion_paths
            for fact_id in path.required_fact_ids
        }
        if referenced - known:
            raise ValueError(
                "completion paths reference unknown specification facts: "
                + ", ".join(sorted(referenced - known))
            )
        return self


class SpecificationTemplateCatalog(CFDCModel):
    schema_version: str = "1.0"
    templates: list[SpecificationTemplate] = Field(min_length=1)
