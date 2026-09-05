from collections import defaultdict

from decisions.constants import (
    CONFIDENCE_BUCKETS,
    MIN_REVIEWS_FOR_INSIGHTS,
    OUTCOME_SCORES,
    STATUS_DRAFT,
    STATUS_LOCKED,
    STATUS_REVIEWED,
)
from decisions.models import Decision


def percent(numerator, denominator):
    if not denominator:
        return 0.0
    return round(numerator / denominator * 100, 1)


def build_calibration_buckets(scored_decisions):
    """Groups decisions by how confident the person was, then checks how often they were right.

    A perfectly calibrated person's 'claimed' and 'actual' columns match. Everyone
    else finds out which direction they lean.
    """
    buckets = []
    for low, high in CONFIDENCE_BUCKETS:
        in_bucket = [item for item in scored_decisions if low <= item["confidence"] < high]
        buckets.append(
            {
                "label": f"{low}-{high - 1 if high <= 100 else 100}%",
                "claimed": (
                    round(sum(item["confidence"] for item in in_bucket) / len(in_bucket), 1) if in_bucket else None
                ),
                "actual": percent(sum(item["score"] for item in in_bucket), len(in_bucket)),
                "count": len(in_bucket),
            }
        )
    return buckets


def build_category_breakdown(scored_decisions):
    grouped = defaultdict(list)
    for item in scored_decisions:
        grouped[item["category"]].append(item)

    breakdown = []
    for category, items in grouped.items():
        breakdown.append(
            {
                "category": category,
                "count": len(items),
                "accuracy": percent(sum(item["score"] for item in items), len(items)),
                "average_confidence": round(sum(item["confidence"] for item in items) / len(items), 1),
            }
        )
    return sorted(breakdown, key=lambda row: row["accuracy"])


def build_challenge_effect(scored_decisions):
    """Does arguing with the AI actually make you better calibrated, or just quieter?"""
    challenged = [item for item in scored_decisions if item["shift"] is not None and item["shift"] != 0]
    unchanged = [item for item in scored_decisions if item["shift"] in (None, 0)]

    def calibration_gap(items):
        if not items:
            return None
        claimed = sum(item["confidence"] for item in items) / len(items)
        actual = sum(item["score"] for item in items) / len(items) * 100
        return round(claimed - actual, 1)

    return {
        "moved_count": len(challenged),
        "unmoved_count": len(unchanged),
        "average_shift": round(sum(item["shift"] for item in challenged) / len(challenged), 1) if challenged else None,
        "gap_when_moved": calibration_gap(challenged),
        "gap_when_unmoved": calibration_gap(unchanged),
    }


def build_track_record(user):
    """The single source of truth for every number the app shows about a user."""
    decisions = (
        Decision.objects.filter(user=user, is_deleted=False)
        .select_related("review")
        .only(
            "category",
            "status",
            "initial_confidence",
            "final_confidence",
            "review__outcome",
        )
    )

    counts = {STATUS_DRAFT: 0, STATUS_LOCKED: 0, STATUS_REVIEWED: 0}
    scored_decisions = []

    for decision in decisions:
        counts[decision.status] = counts.get(decision.status, 0) + 1
        review = getattr(decision, "review", None)
        if decision.status != STATUS_REVIEWED or review is None:
            continue
        scored_decisions.append(
            {
                "category": decision.category,
                "confidence": decision.scored_confidence,
                "score": OUTCOME_SCORES[review.outcome],
                "shift": (
                    None
                    if decision.final_confidence is None
                    else decision.final_confidence - decision.initial_confidence
                ),
            }
        )

    reviewed_count = len(scored_decisions)
    accuracy = percent(sum(item["score"] for item in scored_decisions), reviewed_count)
    average_confidence = (
        round(sum(item["confidence"] for item in scored_decisions) / reviewed_count, 1) if reviewed_count else 0.0
    )
    # Brier score: mean squared distance between what you claimed and what happened.
    # 0.0 is perfect, 0.25 is a coin flip, 1.0 is confidently wrong every time.
    brier = (
        round(
            sum((item["confidence"] / 100 - item["score"]) ** 2 for item in scored_decisions) / reviewed_count,
            3,
        )
        if reviewed_count
        else None
    )
    category_breakdown = build_category_breakdown(scored_decisions)

    return {
        "total_decisions": sum(counts.values()),
        "draft_count": counts.get(STATUS_DRAFT, 0),
        "locked_count": counts.get(STATUS_LOCKED, 0),
        "reviewed_count": reviewed_count,
        "accuracy_percent": accuracy,
        "average_confidence": average_confidence,
        "calibration_gap": round(average_confidence - accuracy, 1),
        "brier_score": brier,
        "has_enough_data": reviewed_count >= MIN_REVIEWS_FOR_INSIGHTS,
        "minimum_reviews": MIN_REVIEWS_FOR_INSIGHTS,
        "buckets": build_calibration_buckets(scored_decisions),
        "by_category": category_breakdown,
        "weakest_category": category_breakdown[0]["category"] if category_breakdown else None,
        "challenge_effect": build_challenge_effect(scored_decisions),
    }
