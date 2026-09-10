from cfdc.specifications import default_specification_template_catalog


def test_first_order_template_calls_user_ranges_simulation_boundaries():
    template = next(
        item
        for item in default_specification_template_catalog().templates
        if item.method_profile_id == "first_order_lag"
    )
    rendered = " ".join(
        [
            template.user_summary,
            *(field.label for field in template.fields),
            *(field.prompt_template for field in template.fields),
            *(field.why_needed for field in template.fields),
        ]
    )

    assert "仿真运行" in rendered
    assert "真实安全范围" not in rendered
    assert "真实执行器" not in rendered
