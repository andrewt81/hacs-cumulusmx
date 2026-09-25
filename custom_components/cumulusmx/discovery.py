"""Rules for recognizing usable values in Cumulus MX web tag responses."""
import math


def numeric_value(payload, tag):
    value = payload.get(tag)
    if value is None or isinstance(value, bool):
        return None
    text = str(value).strip()
    if not text or "web tag error" in text.lower():
        return None
    try:
        number = float(text.replace(",", "."))
    except ValueError:
        return None
    if not math.isfinite(number) or number == -999:
        return None
    return number


def available_tags(payload, candidates):
    return {key for key in candidates if numeric_value(payload, key) is not None}
