from __future__ import annotations

from cfdc.models import (
    ArchetypeClass,
    ControlMethodProfile,
    ControlMethodProfileCatalog,
)


def _method(
    profile_id: str,
    compatible_class: ArchetypeClass,
    semantic_description: str,
    feature_bundle_id: str,
    required_feature_ids: list[str],
    controller_template_id: str,
    experiment_primitives: list[str],
    tunable_gain_names: list[str],
    tracking_ids: list[str],
) -> ControlMethodProfile:
    return ControlMethodProfile(
        profile_id=profile_id,
        compatible_class=compatible_class,
        semantic_description=semantic_description,
        feature_bundle_id=feature_bundle_id,
        required_feature_ids=required_feature_ids,
        controller_template_id=controller_template_id,
        experiment_primitives=experiment_primitives,
        tunable_gain_names=tunable_gain_names,
        tracking_ids=tracking_ids,
    )


def default_control_method_profile_catalog() -> ControlMethodProfileCatalog:
    """Return the method view generated from the canonical knowledge registry."""

    from cfdc.knowledge import profile_definitions

    return ControlMethodProfileCatalog(
        profiles=[
            _method(
                item.profile_id,
                ArchetypeClass(item.compatible_class),
                item.semantic_description,
                item.feature_bundle_id,
                list(item.required_feature_ids),
                item.controller_template_id,
                list(item.experiment_primitives),
                list(item.tunable_gain_names),
                list(item.tracking_ids),
            )
            for item in profile_definitions()
        ]
    )
