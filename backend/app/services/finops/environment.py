"""Non-production environment detection — via tags first, resource name as
a fallback. Used by the non-prod scheduling rule.
"""

ENV_TAG_KEYS = ["Environment", "environment", "Env", "env"]
NON_PROD_VALUES = {"dev", "development", "staging", "stage", "test", "qa", "sandbox"}
NON_PROD_NAME_HINTS = ["dev", "staging", "stage", "test", "qa", "sandbox"]

TAG_MATCH_CONFIDENCE = 0.9
NAME_MATCH_CONFIDENCE = 0.65


def is_non_production(resource_id: str, tags: dict[str, str]) -> tuple[bool, float]:
    """Returns (is_non_prod, confidence). An explicit environment tag is a
    much stronger signal than a name that merely looks non-prod."""
    for key in ENV_TAG_KEYS:
        value = tags.get(key)
        if value and value.strip().lower() in NON_PROD_VALUES:
            return True, TAG_MATCH_CONFIDENCE

    name = (tags.get("Name") or resource_id).lower()
    if any(hint in name for hint in NON_PROD_NAME_HINTS):
        return True, NAME_MATCH_CONFIDENCE

    return False, 0.0
