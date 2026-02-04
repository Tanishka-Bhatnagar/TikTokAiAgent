def validate_campaign_name(name: str):
    if len(name.strip()) < 3:
        return False, "Campaign name must be at least 3 characters long."
    return True, None


def validate_objective(obj: str):
    if obj not in ["Traffic", "Conversions"]:
        return False, "Objective must be either 'Traffic' or 'Conversions'."
    return True, None


def validate_ad_text(text: str):
    if not text.strip():
        return False, "Ad text is required."
    if len(text) > 100:
        return False, "Ad text must be 100 characters or fewer."
    return True, None


def validate_cta(cta: str):
    if not cta.strip():
        return False, "CTA is required."
    return True, None
