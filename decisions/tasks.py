import logging

from celery import shared_task
from django.utils import timezone

from decisions.constants import CHALLENGE_READY, STATUS_LOCKED
from decisions.models import Challenge, Decision
from decisions.utils import build_challenge_payload, create_review_due_notification
from reckon.ai import get_provider

logger = logging.getLogger(__name__)


@shared_task
def generate_challenge(decision_uuid):
    """Asks the configured AI provider to argue against a decision."""
    decision = Decision.objects.get(uuid=decision_uuid, is_deleted=False)
    provider = get_provider()
    result = provider.challenge(build_challenge_payload(decision))

    Challenge.objects.update_or_create(
        decision=decision,
        defaults={
            "status": CHALLENGE_READY,
            "counterarguments": result["counterarguments"],
            "blind_spots": result["blind_spots"],
            "failure_conditions": result["failure_conditions"],
            "sharpest_question": result["sharpest_question"],
            "provider": provider.name,
        },
    )
    logger.info("Generated challenge for decision %s via %s", decision_uuid, provider.name)
    return str(decision_uuid)


@shared_task
def raise_due_reviews():
    """Every locked decision whose review date has arrived gets one notification."""
    due_decisions = Decision.objects.filter(
        status=STATUS_LOCKED,
        review_date__lte=timezone.localdate(),
        is_deleted=False,
    ).select_related("user")

    created_count = sum(create_review_due_notification(decision) for decision in due_decisions)
    logger.info("Raised %s review notifications", created_count)
    return {"due": due_decisions.count(), "created": created_count}
