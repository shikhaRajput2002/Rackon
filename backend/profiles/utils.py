from decimal import ROUND_HALF_UP, Decimal

from profiles.constants import (
    CURRENCY_SYMBOLS,
    EMERGENCY_FUND_FLOOR_MONTHS,
    EMERGENCY_FUND_MONTHS,
    EMI_COMFORTABLE_CEILING,
    EMI_TIGHT_CEILING,
    LOAN_ANNUAL_RATE,
    LOAN_TENURE_MONTHS,
    MONTHS_IN_YEAR,
    STRAIN_COMFORTABLE,
    STRAIN_STRAINED,
    STRAIN_TIGHT,
)

ZERO = Decimal("0")
CENTS = Decimal("0.01")
TENTHS = Decimal("0.1")


def money(value):
    """Rounds to two places and hands back a float the API can serialise."""
    return float(Decimal(value).quantize(CENTS, rounding=ROUND_HALF_UP))


def ratio(value):
    """One decimal place — percentages and month counts read better that way."""
    return float(Decimal(value).quantize(TENTHS, rounding=ROUND_HALF_UP))


def currency_symbol(currency):
    return CURRENCY_SYMBOLS.get(currency, currency)


def format_amount(value, currency="INR"):
    """Indian grouping (1,20,000) for rupees, thousands grouping otherwise."""
    symbol = currency_symbol(currency)
    whole = int(Decimal(value).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    if currency != "INR":
        return f"{symbol}{whole:,}"

    digits = str(abs(whole))
    if len(digits) > 3:
        head, tail = digits[:-3], digits[-3:]
        parts = []
        while len(head) > 2:
            parts.insert(0, head[-2:])
            head = head[:-2]
        if head:
            parts.insert(0, head)
        digits = ",".join(parts) + "," + tail
    sign = "-" if whole < 0 else ""
    return f"{sign}{symbol}{digits}"


def monthly_disposable(profile):
    """What is actually free each month, after living costs and existing loans."""
    return (profile.monthly_income or ZERO) - (profile.monthly_expenses or ZERO) - (profile.existing_emi or ZERO)


def emergency_fund_months(profile):
    """How many months of expenses the current savings would cover."""
    expenses = profile.monthly_expenses or ZERO
    if expenses <= ZERO:
        return None
    return (profile.current_savings or ZERO) / expenses


def estimate_emi(principal, annual_rate=LOAN_ANNUAL_RATE, months=LOAN_TENURE_MONTHS):
    """Standard reducing-balance EMI."""
    monthly_rate = Decimal(annual_rate) / Decimal(100) / Decimal(MONTHS_IN_YEAR)
    if monthly_rate == ZERO:
        return Decimal(principal) / Decimal(months)
    growth = (Decimal(1) + monthly_rate) ** months
    return Decimal(principal) * monthly_rate * growth / (growth - Decimal(1))


def classify_strain(total_emi, income):
    """Bands on total loan payments as a share of income. Rules of thumb, not rules."""
    if income <= ZERO:
        return STRAIN_STRAINED
    share = total_emi / income * Decimal(100)
    if share <= EMI_COMFORTABLE_CEILING:
        return STRAIN_COMFORTABLE
    if share <= EMI_TIGHT_CEILING:
        return STRAIN_TIGHT
    return STRAIN_STRAINED


def assess_purchase(profile, amount):
    """
    Works out what a purchase of ``amount`` does to this person's month and to
    their safety net, both ways of paying for it. Returns numbers only — what to
    do with them is the reader's call.
    """
    amount = Decimal(amount)
    income = profile.monthly_income or ZERO
    expenses = profile.monthly_expenses or ZERO
    savings = profile.current_savings or ZERO
    existing_emi = profile.existing_emi or ZERO
    disposable = monthly_disposable(profile)

    emi = estimate_emi(amount)
    total_emi = emi + existing_emi
    disposable_after_emi = disposable - emi

    savings_after = savings - amount
    months_covered_after = (savings_after / expenses) if expenses > ZERO else None
    months_to_save_up = (amount / disposable) if disposable > ZERO else None

    return {
        "currency": profile.currency,
        "amount": money(amount),
        "monthly_income": money(income),
        "monthly_disposable": money(disposable),
        "strain": classify_strain(total_emi, income),
        "financed": {
            "emi": money(emi),
            "tenure_months": LOAN_TENURE_MONTHS,
            "annual_rate": float(LOAN_ANNUAL_RATE),
            "total_paid": money(emi * LOAN_TENURE_MONTHS),
            "total_interest": money(emi * LOAN_TENURE_MONTHS - amount),
            "emi_percent_of_income": ratio(emi / income * 100) if income > ZERO else None,
            "all_emis_percent_of_income": ratio(total_emi / income * 100) if income > ZERO else None,
            "disposable_after_emi": money(disposable_after_emi),
            "fits_in_disposable": disposable_after_emi > ZERO,
        },
        "upfront": {
            "savings_now": money(savings),
            "savings_after": money(savings_after),
            "affordable_in_cash": savings_after >= ZERO,
            "emergency_months_after": ratio(months_covered_after) if months_covered_after is not None else None,
            "keeps_emergency_fund": (
                months_covered_after >= EMERGENCY_FUND_FLOOR_MONTHS if months_covered_after is not None else False
            ),
            "months_to_save_up": ratio(months_to_save_up) if months_to_save_up is not None else None,
        },
        "assumptions": {
            "emergency_fund_target_months": EMERGENCY_FUND_MONTHS,
            "emergency_fund_floor_months": EMERGENCY_FUND_FLOOR_MONTHS,
            "loan_rate_percent": float(LOAN_ANNUAL_RATE),
            "loan_tenure_months": LOAN_TENURE_MONTHS,
        },
    }


def build_profile_context(profile):
    """The compact dict every AI provider receives instead of the model object."""
    if profile is None:
        return {"is_complete": False}

    fund_months = emergency_fund_months(profile)
    return {
        "is_complete": profile.is_complete,
        "currency": profile.currency,
        "age": profile.age,
        "city": profile.city,
        "dependents": profile.dependents,
        "employment_type": profile.employment_type,
        "risk_appetite": profile.risk_appetite,
        "goals": profile.goals,
        "monthly_income": money(profile.monthly_income) if profile.monthly_income is not None else None,
        "monthly_expenses": money(profile.monthly_expenses) if profile.monthly_expenses is not None else None,
        "current_savings": money(profile.current_savings) if profile.current_savings is not None else None,
        "existing_emi": money(profile.existing_emi or ZERO),
        "monthly_disposable": money(monthly_disposable(profile)) if profile.is_complete else None,
        "emergency_fund_months": ratio(fund_months) if fund_months is not None else None,
    }
