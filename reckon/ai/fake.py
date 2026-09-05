import random
from typing import Dict

from advisor.constants import CONFIDENCE_BY_STRAIN, TOPIC_MONEY, TOPIC_TRACK_RECORD
from advisor.utils import build_suggested_title
from reckon.ai.base import AIProvider
from profiles.constants import STRAIN_COMFORTABLE, STRAIN_TIGHT
from profiles.utils import format_amount

COUNTERARGUMENTS_BY_CATEGORY = {
    "CAREER": [
        "The upside you are picturing depends on a manager and a team you have not worked with yet.",
        "You are comparing your current job's known problems against a new job's unknown ones.",
        "Titles and scope promised during hiring are the first things to change after you join.",
        "If this is partly about escaping something, the thing you are escaping may follow you.",
    ],
    "MONEY": [
        "You are treating a projected return as a fact, when it is a range with a bad tail.",
        "The downside case here is not 'slower growth', it is 'this money is locked up when you need it'.",
        "Fees, taxes and the spread quietly eat a chunk of the gain you are counting on.",
        "You would not make this call if the amount were ten times larger, which suggests it is not principled.",
    ],
    "PRODUCT": [
        "You are solving a problem you have personally felt, which is not evidence anyone else feels it.",
        "The build estimate assumes nothing else breaks and nobody asks you for anything else.",
        "Shipping this closes off the simpler version you could have tested in a week.",
        "The users who asked for this are the loudest ones, not necessarily the most numerous.",
    ],
    "HEALTH": [
        "The plan works on a good week; you have not designed it for a bad one.",
        "You are relying on motivation, which is the resource most likely to be gone in three weeks.",
        "Past attempts at this failed for a specific reason you have not named or fixed.",
    ],
    "RELATIONSHIP": [
        "You are optimising for how this conversation goes, not for where things stand in six months.",
        "You are assuming the other person reads your intent the way you intend it.",
        "Waiting feels safe, but the cost of waiting is real and you have not priced it.",
    ],
    "LEARNING": [
        "Starting is cheap and you are good at it; finishing is the part that has failed before.",
        "The time this needs has to come out of something. You have not said what.",
        "You may be buying the feeling of progress rather than the skill itself.",
    ],
    "OTHER": [
        "The strongest reason for this is that you have already half-decided and want to stop deliberating.",
        "You have described what happens if it works, but not what you do if it does not.",
        "This is reversible in theory and expensive to reverse in practice.",
    ],
}

BLIND_SPOTS = [
    "You have not written down what would make you change your mind. That usually means nothing would.",
    "There is no cost attached to being wrong here, so nothing forces you to be honest about the odds.",
    "You are weighing this against doing nothing, but doing nothing is also a choice with a price.",
    "Everyone you discussed this with is someone who already agrees with you.",
    "The timeline assumes you get uninterrupted attention, which you have not had in months.",
    "You are counting a one-off effort as if it were a habit you already have.",
    "Nobody in this plan is responsible for stopping it if it goes badly.",
]

FAILURE_CONDITIONS = [
    "It takes twice as long as you planned, and the reason it does is boring and unavoidable.",
    "The thing you are counting on stays true for two months and then quietly stops being true.",
    "You get the outcome you asked for and discover it was not the outcome you wanted.",
    "A second, unrelated commitment lands in the same window and you have no slack.",
    "The person whose cooperation this needs is not as invested as you assumed.",
    "You are right about the direction and wrong about the timing, which costs the same as being wrong.",
]

SHARPEST_QUESTIONS = [
    "What would have to be true in six months for you to call this a mistake?",
    "If you had to make this call with half the information, would your answer change?",
    "Who benefits if you are wrong, and have you spoken to them?",
    "What is the cheapest version of this that would still teach you something?",
    "Are you deciding this now because it is the right time, or because you are tired of thinking about it?",
]

OVERCONFIDENCE_NUDGE = (
    "You put this at {confidence}%. Decisions in this category rarely justify that number, "
    "and you have not listed a single thing that would move it down."
)
UNDERCONFIDENCE_NUDGE = (
    "You put this at {confidence}%, which is low enough that the real question is not whether "
    "to do it, but why you are doing it at all."
)


class FakeProvider(AIProvider):
    """
    Offline provider. Costs nothing, needs no key, and never touches the network.

    Output is seeded from the decision's uuid, so a given decision always gets the
    same challenge back. That keeps the app deterministic for tests and demos.
    """

    name = "fake"

    def challenge(self, decision: Dict) -> Dict:
        rng = random.Random(str(decision["uuid"]))
        category = decision.get("category", "OTHER")
        pool = COUNTERARGUMENTS_BY_CATEGORY.get(category, COUNTERARGUMENTS_BY_CATEGORY["OTHER"])

        confidence = decision["initial_confidence"]
        if confidence >= 75:
            nudge = OVERCONFIDENCE_NUDGE.format(confidence=confidence)
        elif confidence <= 40:
            nudge = UNDERCONFIDENCE_NUDGE.format(confidence=confidence)
        else:
            nudge = (
                f"At {confidence}% you are genuinely unsure, so the deciding factor is "
                f"whichever way you are wrong more cheaply."
            )

        return {
            "counterarguments": rng.sample(pool, min(3, len(pool))) + [nudge],
            "blind_spots": rng.sample(BLIND_SPOTS, 3),
            "failure_conditions": rng.sample(FAILURE_CONDITIONS, 3),
            "sharpest_question": rng.choice(SHARPEST_QUESTIONS),
        }

    def advise(self, question, topic, profile, track_record, assessment, history):
        if topic == TOPIC_TRACK_RECORD:
            return track_record_advice(track_record)
        if topic == TOPIC_MONEY and assessment:
            return money_advice(question, profile, track_record, assessment)
        return general_advice(question, profile, track_record)


def calibration_note(track_record):
    """One sentence about their own bias, or nothing if there is not enough data."""
    if not track_record.get("has_enough_data"):
        return None
    gap = track_record.get("calibration_gap", 0)
    if gap > 5:
        return (
            f"For what it is worth, you run about {gap} points overconfident across "
            f"{track_record['reviewed_count']} scored decisions — worth shaving whatever number you land on."
        )
    if gap < -5:
        return (
            f"Your track record says you are underconfident by about {abs(gap)} points, so you may be "
            "talking yourself out of this more than the facts warrant."
        )
    return "Your confidence has tracked reality closely so far, so trust your own read here."


def category_note(track_record, category):
    for row in track_record.get("by_category", []):
        if row["category"] == category and row["count"] >= 2 and row["accuracy"] < 50:
            return (
                f"{category.title()} is your weakest category — right {row['accuracy']}% of the time "
                f"across {row['count']} decisions."
            )
    return None


def money_advice(question, profile, track_record, assessment):
    currency = assessment["currency"]
    amount = assessment["amount"]
    income = assessment["monthly_income"]
    financed = assessment["financed"]
    upfront = assessment["upfront"]
    assumptions = assessment["assumptions"]
    strain = assessment["strain"]

    def show(value):
        return format_amount(value, currency)

    ratio = round(amount / income, 1) if income else None
    sentences = []
    if ratio:
        sentences.append(f"{show(amount)} is about {ratio}× your monthly income.")
    sentences.append(
        f"Financed over {financed['tenure_months']} months at {assumptions['loan_rate_percent']}%, "
        f"the EMI is {show(financed['emi'])} — {financed['emi_percent_of_income']}% of what you earn, "
        f"leaving {show(financed['disposable_after_emi'])} free each month."
    )
    if upfront["affordable_in_cash"]:
        sentences.append(
            f"Paying cash instead takes you from {show(upfront['savings_now'])} to "
            f"{show(upfront['savings_after'])}, which is {upfront['emergency_months_after']} months of "
            f"expenses rather than the {assumptions['emergency_fund_target_months']} you would want behind you."
        )
    else:
        sentences.append(
            f"You cannot cover this from savings — {show(upfront['savings_now'])} against "
            f"{show(amount)} — so it is the loan or waiting."
        )

    numbers = [
        {
            "label": "Monthly EMI",
            "value": show(financed["emi"]),
            "note": f"{financed['tenure_months']} months at {assumptions['loan_rate_percent']}%",
        },
        {
            "label": "Share of income",
            "value": f"{financed['emi_percent_of_income']}%",
            "note": f"all loans together: {financed['all_emis_percent_of_income']}%",
        },
        {
            "label": "Free each month after",
            "value": show(financed["disposable_after_emi"]),
            "note": "once living costs and existing EMIs are paid",
        },
        {
            "label": "Interest over the term",
            "value": show(financed["total_interest"]),
            "note": f"total outlay {show(financed['total_paid'])}",
        },
        {
            "label": "Savings if paid in cash",
            "value": show(upfront["savings_after"]),
            "note": (
                f"{upfront['emergency_months_after']} months of expenses"
                if upfront["emergency_months_after"] is not None
                else "before any cushion"
            ),
        },
    ]
    if upfront["months_to_save_up"] is not None:
        numbers.append(
            {
                "label": "Or save up for it",
                "value": f"{upfront['months_to_save_up']} months",
                "note": "at your current spare income, buying nothing else",
            }
        )

    considerations = []
    if strain == STRAIN_COMFORTABLE:
        considerations.append(
            f"At {financed['all_emis_percent_of_income']}% of income going to loan payments, this sits "
            "inside the range most budgets absorb without noticing."
        )
        considerations.append(
            f"So the real question is not whether you can pay it, but what else that "
            f"{show(financed['emi'])} a month was going to do."
        )
    elif strain == STRAIN_TIGHT:
        considerations.append(
            f"{financed['all_emis_percent_of_income']}% of income on loan payments is workable, but it "
            "leaves little slack for a month that goes wrong."
        )
    else:
        considerations.append(
            f"At {financed['all_emis_percent_of_income']}% of income on loan repayments, one interrupted "
            "month of earnings turns this into a problem rather than an inconvenience."
        )

    if upfront["affordable_in_cash"] and not upfront["keeps_emergency_fund"]:
        considerations.append(
            f"Paying cash drops your cushion to {upfront['emergency_months_after']} months, under the "
            f"{assumptions['emergency_fund_floor_months']}-month floor most people want."
        )
    elif upfront["keeps_emergency_fund"]:
        considerations.append(
            f"Paying cash still leaves {upfront['emergency_months_after']} months of expenses in reserve, "
            "which clears the usual floor."
        )

    dependents = profile.get("dependents")
    if dependents:
        considerations.append(
            f"With {dependents} {'dependant' if dependents == 1 else 'dependants'}, the cost of being "
            "wrong here lands on more than you."
        )

    note = category_note(track_record, "MONEY") or calibration_note(track_record)
    if note:
        considerations.append(note)

    watch_outs = [
        "This is the sticker price only — insurance, servicing, fuel and accessories are not in any of it.",
        f"The EMI assumes {assumptions['loan_tenure_months']} months at "
        f"{assumptions['loan_rate_percent']}%. A longer tenure lowers the monthly figure and raises the interest a lot.",
        "Nothing here knows what you would give up to afford it. That part is yours.",
    ]

    return {
        "answer": " ".join(sentences),
        "numbers": numbers,
        "considerations": considerations,
        "watch_outs": watch_outs,
        "suggested_decision": {
            "title": build_suggested_title(question),
            "category": "MONEY",
            "chosen_option": "Go ahead with it",
            "expected_outcome": (
                f"I pay {show(financed['emi'])} a month without resenting it, and nothing I actually "
                "needed got squeezed out."
            ),
            "initial_confidence": CONFIDENCE_BY_STRAIN.get(strain, 50),
        },
    }


def track_record_advice(track_record):
    reviewed = track_record.get("reviewed_count", 0)
    if reviewed < track_record.get("minimum_reviews", 3):
        return {
            "answer": (
                f"You have {reviewed} scored decision(s), which is not enough to say anything honest about "
                "your track record. Ask again once five or six have been through a review — patterns before "
                "then are noise."
            ),
            "numbers": [],
            "considerations": [],
            "watch_outs": [],
            "suggested_decision": {},
        }

    accuracy = track_record["accuracy_percent"]
    claimed = track_record["average_confidence"]
    gap = track_record["calibration_gap"]
    weakest = track_record.get("weakest_category") or "—"

    verdict = (
        f"That is a {gap} point overconfidence gap."
        if gap > 5
        else f"You are underconfident by {abs(gap)} points." if gap < -5 else "That is well calibrated."
    )

    return {
        "answer": (
            f"Across {reviewed} scored decisions you were right {accuracy}% of the time while claiming "
            f"{claimed}% confidence on average. {verdict} Your weakest area is {weakest.lower()}."
        ),
        "numbers": [
            {"label": "You were right", "value": f"{accuracy}%", "note": f"across {reviewed} decisions"},
            {"label": "You claimed", "value": f"{claimed}%", "note": "average confidence"},
            {
                "label": "Brier score",
                "value": str(track_record.get("brier_score")),
                "note": "0 perfect, 0.25 a coin flip",
            },
        ],
        "considerations": [
            f"When you feel sure about {weakest.lower()}, that is exactly where the record says to slow down.",
            "The gap only shrinks if you keep scoring decisions honestly, including the ones you got wrong.",
        ],
        "watch_outs": [],
        "suggested_decision": {},
    }


def general_advice(question, profile, track_record):
    considerations = [
        "Write down now what would make this a mistake. If nothing would, you have already decided.",
        "Ask what the smallest version of this is — the one that tells you the same thing in two weeks instead of six months.",
        "Whatever this takes has to come out of something else. Name the something else.",
    ]
    dependents = profile.get("dependents")
    if dependents:
        considerations.append(
            f"With {dependents} {'dependant' if dependents == 1 else 'dependants'}, factor in whose time "
            "this spends besides yours."
        )
    note = calibration_note(track_record)
    if note:
        considerations.append(note)

    return {
        "answer": (
            "There is no arithmetic to run on this one, so the useful move is to make it falsifiable. "
            "Decide now what you would expect to see if it is working, and when you would check — then log "
            "it, so future you gets a straight answer instead of a story."
        ),
        "numbers": [],
        "considerations": considerations,
        "watch_outs": [
            "Enthusiasm at the start is not evidence. Most things like this fail at week three, not week one.",
        ],
        "suggested_decision": {
            "title": build_suggested_title(question),
            "category": "OTHER",
            "chosen_option": "Go ahead with it",
            "expected_outcome": "Describe what you would see in a few months if this worked.",
            "initial_confidence": 60,
        },
    }
