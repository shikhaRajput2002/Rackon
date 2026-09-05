CHALLENGE_SYSTEM_PROMPT = """You are a rigorous devil's advocate reviewing a decision \
someone is about to make. Your job is to find the strongest case against it, not to be \
agreeable and not to be contrarian for its own sake.

Rules:
- Argue against the choice they are leaning toward, using their own stated reasoning.
- Name the assumptions they are treating as facts.
- Be concrete. "This might not work" is useless; "this fails if hiring takes 3 months \
instead of 1" is useful.
- Never tell them what to decide. You surface what they have not considered.
- Each item is one sentence, under 30 words."""

CHALLENGE_SCHEMA = {
    "type": "object",
    "properties": {
        "counterarguments": {"type": "array", "items": {"type": "string"}},
        "blind_spots": {"type": "array", "items": {"type": "string"}},
        "failure_conditions": {"type": "array", "items": {"type": "string"}},
        "sharpest_question": {"type": "string"},
    },
    "required": ["counterarguments", "blind_spots", "failure_conditions", "sharpest_question"],
    "additionalProperties": False,
}

ADVISOR_SYSTEM_PROMPT = """You help one person think through decisions they are weighing. \
You have their financial profile and the track record of decisions they have logged before.

Rules:
- Never tell them what to do. Lay out what the numbers say and what the trade-off is, \
then let them choose. "This costs you four months of your safety net" beats "don't buy it".
- When an `assessment` object is supplied, every figure you cite must come from it. Do not \
compute your own numbers and do not estimate prices.
- You are not a licensed financial adviser and must not present yourself as one. Affordability \
arithmetic and things to consider are fine; product recommendations and investment advice are not.
- Be concrete and short. No pep talk, no hedging, no restating the question.
- If their own track record is relevant — they are overconfident in this category, say — bring it up.
- `answer` is at most 140 words of plain prose. Each list item is one sentence under 25 words.
- `suggested_decision.initial_confidence` is your read of how likely this is to work out, 0-100."""

ADVISOR_SCHEMA = {
    "type": "object",
    "properties": {
        "answer": {"type": "string"},
        "numbers": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "label": {"type": "string"},
                    "value": {"type": "string"},
                    "note": {"type": "string"},
                },
                "required": ["label", "value", "note"],
                "additionalProperties": False,
            },
        },
        "considerations": {"type": "array", "items": {"type": "string"}},
        "watch_outs": {"type": "array", "items": {"type": "string"}},
        "suggested_decision": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "category": {
                    "type": "string",
                    "enum": ["CAREER", "MONEY", "PRODUCT", "HEALTH", "RELATIONSHIP", "LEARNING", "OTHER"],
                },
                "chosen_option": {"type": "string"},
                "expected_outcome": {"type": "string"},
                "initial_confidence": {"type": "integer"},
            },
            "required": ["title", "category", "chosen_option", "expected_outcome", "initial_confidence"],
            "additionalProperties": False,
        },
    },
    "required": ["answer", "numbers", "considerations", "watch_outs", "suggested_decision"],
    "additionalProperties": False,
}


def build_challenge_prompt(decision: dict) -> str:
    options = "\n".join(f"- {option}" for option in decision.get("options_considered") or [])
    return (
        f"Decision: {decision['title']}\n"
        f"Category: {decision['category']}\n\n"
        f"Their reasoning:\n{decision['context']}\n\n"
        f"Options they weighed:\n{options or '- (none recorded)'}\n\n"
        f"What they are leaning toward: {decision['chosen_option']}\n"
        f"What they expect to happen: {decision['expected_outcome']}\n"
        f"How confident they are: {decision['initial_confidence']}%\n\n"
        "Make the strongest case against this."
    )
