import json

from cfdc.audit import sanitize_for_audit


def test_sanitizer_redacts_nested_keys_literals_bearer_and_url_credentials():
    sanitized = sanitize_for_audit(
        {
            "nested": {
                "Authorization": "Bearer abc.def",
                "note": (
                    "key=MYSECRET https://user:pass@example.test/a?api_key=q&ok=1"
                ),
            }
        },
        secret_literals=["MYSECRET"],
    )
    rendered = json.dumps(sanitized)
    for secret in ("abc.def", "MYSECRET", "user:pass", "api_key=q"):
        assert secret not in rendered
    assert "[REDACTED]" in rendered
