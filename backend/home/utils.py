from home.constants import DAILY_QUOTES


def quote_for_date(day):
    """Same quote all day, a different one tomorrow, no randomness to re-roll."""
    text, author = DAILY_QUOTES[day.toordinal() % len(DAILY_QUOTES)]
    return {"text": text, "author": author}
