from reckon.exceptions import AppError

PROFILE_REQUIRED_FOR_MONEY = AppError(
    "PROFILE_REQUIRED_FOR_MONEY",
    "Add your income, monthly expenses and savings first — without them this is just a guess.",
    status=400,
)
AMOUNT_REQUIRED = AppError(
    "AMOUNT_REQUIRED",
    "Tell me roughly what it costs and I can work out what it does to your month.",
    status=400,
)
