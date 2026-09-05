from reckon.exceptions import AppError

PROFILE_INCOMPLETE = AppError(
    "PROFILE_INCOMPLETE",
    "Add your income, monthly expenses and savings before asking for advice.",
    status=400,
)
