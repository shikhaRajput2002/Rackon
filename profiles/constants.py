from decimal import Decimal

EMPLOYMENT_SALARIED = "SALARIED"
EMPLOYMENT_SELF_EMPLOYED = "SELF_EMPLOYED"
EMPLOYMENT_STUDENT = "STUDENT"
EMPLOYMENT_BETWEEN_JOBS = "BETWEEN_JOBS"

EMPLOYMENT_CHOICES = (
    (EMPLOYMENT_SALARIED, "Salaried"),
    (EMPLOYMENT_SELF_EMPLOYED, "Self-employed"),
    (EMPLOYMENT_STUDENT, "Student"),
    (EMPLOYMENT_BETWEEN_JOBS, "Between jobs"),
)

RISK_LOW = "LOW"
RISK_MEDIUM = "MEDIUM"
RISK_HIGH = "HIGH"

RISK_CHOICES = (
    (RISK_LOW, "Cautious"),
    (RISK_MEDIUM, "Balanced"),
    (RISK_HIGH, "Comfortable with risk"),
)

CURRENCY_SYMBOLS = {
    "INR": "₹",
    "USD": "$",
    "EUR": "€",
    "GBP": "£",
}
DEFAULT_CURRENCY = "INR"

# Assumptions used when someone asks about financing a purchase. Shown in the
# response so the arithmetic is never a black box.
LOAN_ANNUAL_RATE = Decimal("9.5")
LOAN_TENURE_MONTHS = 36
MONTHS_IN_YEAR = 12

# A widely used rule of thumb, not a law: keep six months of expenses liquid.
EMERGENCY_FUND_MONTHS = 6
EMERGENCY_FUND_FLOOR_MONTHS = 3

# Total monthly loan payments as a share of income.
EMI_COMFORTABLE_CEILING = Decimal("20")
EMI_TIGHT_CEILING = Decimal("35")

STRAIN_COMFORTABLE = "COMFORTABLE"
STRAIN_TIGHT = "TIGHT"
STRAIN_STRAINED = "STRAINED"

REQUIRED_FOR_ADVICE = ("monthly_income", "monthly_expenses", "current_savings")
