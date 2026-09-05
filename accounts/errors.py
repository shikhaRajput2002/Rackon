from reckon.exceptions import AppError

EMAIL_ALREADY_REGISTERED = AppError("EMAIL_ALREADY_REGISTERED", "That email is already registered.", status=400)
INVALID_CREDENTIALS = AppError("INVALID_CREDENTIALS", "Email or password is incorrect.", status=400)
