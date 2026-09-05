ROLE_USER = "user"
ROLE_ASSISTANT = "assistant"

ROLE_CHOICES = (
    (ROLE_USER, "User"),
    (ROLE_ASSISTANT, "Assistant"),
)

TOPIC_MONEY = "MONEY"
TOPIC_TRACK_RECORD = "TRACK_RECORD"
TOPIC_GENERAL = "GENERAL"

TOPIC_CHOICES = (
    (TOPIC_MONEY, "Money"),
    (TOPIC_TRACK_RECORD, "Track record"),
    (TOPIC_GENERAL, "General"),
)

# Suffixes people actually type for Indian amounts.
AMOUNT_MULTIPLIERS = {
    "crore": 10_000_000,
    "crores": 10_000_000,
    "cr": 10_000_000,
    "lakh": 100_000,
    "lakhs": 100_000,
    "lac": 100_000,
    "lacs": 100_000,
    "l": 100_000,
    "k": 1_000,
    "thousand": 1_000,
}

# A bare number this size is an amount; anything smaller needs a suffix or a
# currency marker, so "3 months" is never read as three rupees.
BARE_AMOUNT_FLOOR = 1_000

# Words that mean the number before them was a duration or a measure, not money.
NON_MONEY_UNITS = {
    "month",
    "months",
    "year",
    "years",
    "week",
    "weeks",
    "day",
    "days",
    "hour",
    "hours",
    "minute",
    "minutes",
    "km",
    "kg",
    "percent",
    "%",
    "am",
    "pm",
    "cc",
    "bhp",
    "kmpl",
    "times",
    "people",
    "person",
}

MONEY_KEYWORDS = (
    "buy",
    "buying",
    "purchase",
    "afford",
    "cost",
    "costs",
    "price",
    "loan",
    "emi",
    "invest",
    "spend",
    "spending",
    "salary",
    "rent",
    "bike",
    "car",
    "phone",
    "laptop",
    "house",
    "flat",
    "upgrade",
    "subscription",
    "insurance",
)

TRACK_RECORD_KEYWORDS = (
    "calibrat",
    "overconfident",
    "underconfident",
    "worst at",
    "best at",
    "my record",
    "my track",
    "am i right",
    "accuracy",
    "brier",
    "confidence gap",
    "decisions am i",
    "how often am i",
)

CONFIDENCE_BY_STRAIN = {
    "COMFORTABLE": 70,
    "TIGHT": 55,
    "STRAINED": 40,
}

DEFAULT_REVIEW_DAYS = 90
HISTORY_LIMIT = 20
MAX_QUESTION_LENGTH = 1000
