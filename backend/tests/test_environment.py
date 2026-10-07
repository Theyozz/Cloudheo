from app.services.finops.environment import is_non_production


def test_explicit_tag_match_has_high_confidence():
    non_prod, confidence = is_non_production("i-abc123", {"Environment": "staging"})
    assert non_prod is True
    assert confidence == 0.9


def test_tag_match_is_case_insensitive():
    non_prod, _ = is_non_production("i-abc123", {"Environment": "STAGING"})
    assert non_prod is True


def test_name_hint_has_lower_confidence():
    non_prod, confidence = is_non_production("dev-worker-01", {})
    assert non_prod is True
    assert confidence == 0.65


def test_production_resource_is_not_flagged():
    non_prod, confidence = is_non_production("i-prod123", {"Environment": "production"})
    assert non_prod is False
    assert confidence == 0.0


def test_unrelated_resource_name_is_not_flagged():
    non_prod, _ = is_non_production("payments-api-7", {})
    assert non_prod is False
