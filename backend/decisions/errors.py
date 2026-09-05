from reckon.exceptions import AppError

DECISION_NOT_FOUND = AppError("DECISION_NOT_FOUND", "Decision not found.", status=404)
DECISION_LOCKED = AppError(
    "DECISION_LOCKED",
    "This decision is locked. Locked decisions cannot be edited — that is the point.",
    status=400,
)
DECISION_NOT_LOCKED = AppError("DECISION_NOT_LOCKED", "Lock this decision before reviewing it.", status=400)
DECISION_ALREADY_REVIEWED = AppError(
    "DECISION_ALREADY_REVIEWED", "This decision has already been reviewed.", status=400
)
CHALLENGE_NOT_READY = AppError("CHALLENGE_NOT_READY", "The challenge is still being generated.", status=400)
CHALLENGE_ALREADY_REQUESTED = AppError(
    "CHALLENGE_ALREADY_REQUESTED",
    "A challenge has already been generated for this decision.",
    status=400,
)
REVIEW_DATE_IN_PAST = AppError("REVIEW_DATE_IN_PAST", "The review date must be in the future.", status=400)
NOTIFICATION_NOT_FOUND = AppError("NOTIFICATION_NOT_FOUND", "Notification not found.", status=404)
