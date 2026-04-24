from types import SimpleNamespace

from app.services.automations import rule_matches


def test_rule_matches_tag_condition() -> None:
    rule = SimpleNamespace(condition_config={"tags_any": ["safety"]})

    assert rule_matches(rule=rule, event_payload={"tags": ["safety", "compliance"]}) is True
    assert rule_matches(rule=rule, event_payload={"tags": ["operations"]}) is False


def test_rule_matches_report_type_condition() -> None:
    rule = SimpleNamespace(condition_config={"report_type": "executive"})

    assert rule_matches(rule=rule, event_payload={"report_type": "executive"}) is True
    assert rule_matches(rule=rule, event_payload={"report_type": "operational"}) is False
