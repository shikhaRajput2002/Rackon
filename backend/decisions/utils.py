from decisions.constants import NOTIFICATION_REVIEW_DUE
from decisions.models import Notification


def build_challenge_payload(decision):
    """Flattens a Decision into the plain dict every AI provider accepts."""
    return {
        "uuid": str(decision.uuid),
        "title": decision.title,
        "context": decision.context,
        "options_considered": decision.options_considered,
        "chosen_option": decision.chosen_option,
        "expected_outcome": decision.expected_outcome,
        "category": decision.category,
        "initial_confidence": decision.initial_confidence,
    }


def create_review_due_notification(decision):
    """Idempotent: the unique constraint means re-running the beat task is harmless."""
    _, created = Notification.objects.get_or_create(
        user=decision.user,
        decision=decision,
        kind=NOTIFICATION_REVIEW_DUE,
        defaults={
            "title": f"Time to score: {decision.title}",
            "body": (f"You were {decision.scored_confidence}% confident. " "What actually happened?"),
        },
    )
    return created
