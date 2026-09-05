import re
from decimal import Decimal

from advisor.constants import (
    AMOUNT_MULTIPLIERS,
    BARE_AMOUNT_FLOOR,
    MONEY_KEYWORDS,
    NON_MONEY_UNITS,
    TOPIC_GENERAL,
    TOPIC_MONEY,
    TOPIC_TRACK_RECORD,
    TRACK_RECORD_KEYWORDS,
)

# A symbol is unambiguous. The letters "rs" are not — "Aprilia RS 457" is a
# model name, not four hundred and fifty seven rupees — so text prefixes are
# treated as weak evidence and still have to clear the bare-amount floor.
STRONG_CURRENCY = r"₹|\$"
WEAK_CURRENCY = r"rs\.?|inr|usd"
AMOUNT_PATTERN = re.compile(
    rf"(?P<strong>{STRONG_CURRENCY})?(?P<weak>{WEAK_CURRENCY})?\s*"
    r"(?P<value>[0-9][0-9,]*(?:\.[0-9]+)?)\s*"
    r"(?P<suffix>crores?|cr|lakhs?|lacs?|thousand|[lk])?",
    re.IGNORECASE,
)
NEXT_WORD_PATTERN = re.compile(r"\s*([a-z%]+)", re.IGNORECASE)


def parse_amount(text):
    """
    Pulls a rupee amount out of plain English — "4.2 lakh", "₹4,20,000", "50k".

    Returns the largest credible amount, or None. A bare number only counts if
    it is big enough to be money and is not followed by a unit like "months".
    """
    best = None
    for match in AMOUNT_PATTERN.finditer(text):
        raw = match.group("value").replace(",", "")
        if not raw or raw == ".":
            continue

        suffix = (match.group("suffix") or "").lower()
        has_symbol = bool(match.group("strong"))
        value = Decimal(raw)

        following = NEXT_WORD_PATTERN.match(text, match.end())
        next_word = following.group(1).lower() if following else ""
        if not suffix and next_word in NON_MONEY_UNITS:
            continue

        if suffix:
            value *= Decimal(AMOUNT_MULTIPLIERS[suffix])
        elif not has_symbol and value < BARE_AMOUNT_FLOOR:
            continue

        if best is None or value > best:
            best = value
    return best


def classify_topic(text):
    """Decides which of the three things the person is actually asking about."""
    lowered = text.lower()
    if any(keyword in lowered for keyword in TRACK_RECORD_KEYWORDS):
        return TOPIC_TRACK_RECORD
    if parse_amount(text) is not None or any(keyword in lowered for keyword in MONEY_KEYWORDS):
        return TOPIC_MONEY
    return TOPIC_GENERAL


def build_suggested_title(question):
    """Turns the question into something that reads like a decision title."""
    title = question.strip().rstrip("?").strip()
    for prefix in ("should i ", "should we ", "can i ", "do i ", "is it worth "):
        if title.lower().startswith(prefix):
            title = title[len(prefix) :]
            break
    return (title[:1].upper() + title[1:])[:200]
