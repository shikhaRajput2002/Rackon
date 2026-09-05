from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import User
from decisions.constants import (
    CHALLENGE_READY,
    OUTCOME_MIXED,
    OUTCOME_RIGHT,
    OUTCOME_WRONG,
    STATUS_DRAFT,
    STATUS_LOCKED,
    STATUS_REVIEWED,
)
from decisions.models import Challenge, Decision, Review
from decisions.utils import build_challenge_payload, create_review_due_notification
from notes.models import Note
from profiles.models import Profile
from reckon.ai import get_provider

DEMO_EMAIL = "demo@reckon.local"
DEMO_PASSWORD = "reckon123"

DEMO_PROFILE = {
    "age": 29,
    "city": "Bengaluru",
    "dependents": 1,
    "employment_type": "SALARIED",
    "currency": "INR",
    "monthly_income": 120000,
    "monthly_expenses": 65000,
    "current_savings": 600000,
    "existing_emi": 12000,
    "risk_appetite": "MEDIUM",
    "goals": "Six months of runway before I try anything on my own. Replace the laptop this year.",
}

DEMO_NOTES = [
    (
        "Bike shortlist",
        "Aprilia RS 457 — 4.2L on road. Ninja 400 is 5.2L. Test rode the RS, seat is punishing in traffic.\n"
        "Ask about the 5-year service package before committing to anything.",
        True,
    ),
    (
        "Questions for the 1:1",
        "- Where does the billing rewrite sit after the reorg?\n- Is the second backend hire still funded?\n"
        "- Say the thing about workload before it turns into resentment again.",
        False,
    ),
    (
        "Things I keep re-learning",
        "Every rewrite I have estimated has taken between two and three times as long as I said.\n"
        "Every time I skip the index and go straight to the rewrite, the index was the fix.",
        False,
    ),
    (
        "Swimming",
        "Adult batch at the club is 6:30am Tue/Thu/Sat. 8,000 for three months.\n"
        "The real question is whether I get out of bed, not whether I can afford it.",
        False,
    ),
]

# (title, category, chosen, expected, context, initial, final, status, outcome, what_happened, days_ago)
SEED_DECISIONS = [
    (
        "Rewrite the reporting service in Go",
        "PRODUCT",
        "Rewrite it",
        "Report generation drops from 40s to under 5s and the on-call pages stop.",
        "Reports time out twice a week. The Python service is doing synchronous joins across three DBs. "
        "A rewrite feels cleaner than patching it again.",
        85,
        80,
        STATUS_REVIEWED,
        OUTCOME_WRONG,
        "Took 11 weeks instead of 4. The real bottleneck was a missing index, which we found in week 9. "
        "The Go service is fast, but the index alone would have fixed it.",
        220,
    ),
    (
        "Take the senior role at the smaller company",
        "CAREER",
        "Take it",
        "More ownership, and I ship something end to end within six months.",
        "Current job is stable but I have not learned anything new in a year. The offer is a 10% raise "
        "and a much bigger scope.",
        90,
        75,
        STATUS_REVIEWED,
        OUTCOME_RIGHT,
        "Shipped the billing rewrite in month five. The scope was real. The stability was not, but "
        "that was the trade I chose.",
        400,
    ),
    (
        "Move the whole team to a 4-day week trial",
        "PRODUCT",
        "Run the trial for 3 months",
        "Same output, visibly happier team, and we keep it permanently.",
        "Team is running at about 60% capacity anyway because of meeting load. Compressing might "
        "force better prioritisation.",
        60,
        55,
        STATUS_REVIEWED,
        OUTCOME_MIXED,
        "Output held steady and everyone wanted to keep it. But support coverage broke twice and we "
        "had to put one person on rotation, which undid part of the point.",
        150,
    ),
    (
        "Turn down the consulting contract",
        "MONEY",
        "Turn it down",
        "I protect my evenings and finish the side project instead.",
        "It is 3 months of evening work for a meaningful amount of money. I have a side project I keep "
        "not finishing.",
        70,
        45,
        STATUS_REVIEWED,
        OUTCOME_WRONG,
        "I did not finish the side project. I filled the evenings with nothing in particular. Should "
        "have taken the money.",
        180,
    ),
    (
        "Learn Rust properly instead of skimming it",
        "LEARNING",
        "Commit to 6 weeks, one hour daily",
        "I can read and modify a real Rust codebase without fighting the borrow checker.",
        "I have started Rust three times and quit at chapter 6 each time. This time I want a deadline "
        "and a real project.",
        75,
        60,
        STATUS_REVIEWED,
        OUTCOME_WRONG,
        "Quit at week 3 again. Same reason as before: no actual project needed it, so it stayed abstract.",
        120,
    ),
    (
        "Buy the flat instead of renting another year",
        "MONEY",
        "Buy",
        "Monthly cost is similar and I stop losing rent.",
        "Rent went up 12% again. Prices in the area look flat. I have enough for the deposit but it "
        "clears out my buffer.",
        80,
        65,
        STATUS_REVIEWED,
        OUTCOME_MIXED,
        "The numbers worked out roughly as expected. But the buffer being gone meant a boiler repair "
        "went on a credit card, which I had not modelled.",
        300,
    ),
    (
        "Say no to the reorg proposal",
        "CAREER",
        "Push back formally",
        "Leadership reconsiders, or at least I am on record.",
        "The proposed structure splits the team that owns billing across two managers. I think it will "
        "slow us down badly.",
        55,
        50,
        STATUS_REVIEWED,
        OUTCOME_RIGHT,
        "They kept the structure but gave billing a single owner after two months of exactly the "
        "problems I described.",
        200,
    ),
    (
        "Drop the mobile app and go web-only",
        "PRODUCT",
        "Drop it",
        "We free up two engineers and web conversion barely moves.",
        "The app is 8% of traffic and 40% of our bug reports. Maintaining both is quietly expensive.",
        65,
        70,
        STATUS_REVIEWED,
        OUTCOME_RIGHT,
        "Web conversion went up slightly. The 8% mostly moved to mobile web. Two engineers went to "
        "billing and shipped faster.",
        90,
    ),
    (
        "Start running again, 3 mornings a week",
        "HEALTH",
        "Start Monday",
        "I keep it up for at least 8 weeks.",
        "I have not exercised since January. Mornings are the only time nothing else competes.",
        85,
        70,
        STATUS_REVIEWED,
        OUTCOME_WRONG,
        "Lasted 9 days. The plan assumed I would sleep well, and I did not.",
        60,
    ),
    (
        "Have the direct conversation about workload",
        "RELATIONSHIP",
        "Raise it this week",
        "It gets acknowledged and something actually changes.",
        "I have been absorbing the extra work quietly for two months and I am starting to resent it.",
        50,
        60,
        STATUS_REVIEWED,
        OUTCOME_RIGHT,
        "Went better than expected. Two things moved off my plate the same week. I waited far too long.",
        45,
    ),
    (
        "Migrate CI from Jenkins to GitHub Actions",
        "PRODUCT",
        "Migrate",
        "Build times halve and nobody has to maintain the Jenkins box.",
        "The Jenkins box is a pet nobody wants to touch. Every plugin upgrade is an afternoon.",
        75,
        75,
        STATUS_LOCKED,
        None,
        None,
        None,
    ),
    (
        "Hire a second backend engineer now rather than in Q3",
        "CAREER",
        "Hire now",
        "They are productive before the busy season instead of during it.",
        "We are behind, but hiring takes 3 months and onboarding takes 2. Waiting means they land "
        "exactly when we have no time to onboard them.",
        60,
        50,
        STATUS_LOCKED,
        None,
        None,
        None,
    ),
    (
        "Cancel the conference talk",
        "CAREER",
        "Cancel it",
        "I get three weekends back and nothing bad happens.",
        "I said yes six months ago when the calendar looked empty. It is not empty.",
        45,
        None,
        STATUS_DRAFT,
        None,
        None,
        None,
    ),
]


class Command(BaseCommand):
    help = "Creates a demo account with a realistic decision history."

    def handle(self, *args, **options):
        user = User.objects.filter(email=DEMO_EMAIL).first()
        if user:
            Decision.objects.filter(user=user).delete()
        else:
            user = User.objects.create_user(email=DEMO_EMAIL, password=DEMO_PASSWORD, name="Demo")

        Profile.objects.update_or_create(user=user, defaults=DEMO_PROFILE)

        Note.objects.filter(user=user).delete()
        for title, body, pinned in DEMO_NOTES:
            Note.objects.create(user=user, title=title, body=body, is_pinned=pinned)

        provider = get_provider()
        now = timezone.now()

        for row in SEED_DECISIONS:
            (
                title,
                category,
                chosen,
                expected,
                context,
                initial,
                final,
                status,
                outcome,
                what_happened,
                days_ago,
            ) = row

            created_at = now - timedelta(days=days_ago or 5)
            decision = Decision.objects.create(
                user=user,
                title=title,
                category=category,
                context=context,
                options_considered=[chosen, "Do nothing for now"],
                chosen_option=chosen,
                expected_outcome=expected,
                initial_confidence=initial,
                final_confidence=final,
                review_date=(created_at + timedelta(days=90)).date(),
                status=status,
                locked_at=created_at if status != STATUS_DRAFT else None,
            )

            if final is not None:
                result = provider.challenge(build_challenge_payload(decision))
                Challenge.objects.create(
                    decision=decision,
                    status=CHALLENGE_READY,
                    counterarguments=result["counterarguments"],
                    blind_spots=result["blind_spots"],
                    failure_conditions=result["failure_conditions"],
                    sharpest_question=result["sharpest_question"],
                    provider=provider.name,
                )

            if status == STATUS_REVIEWED:
                Review.objects.create(
                    decision=decision,
                    outcome=outcome,
                    what_happened=what_happened,
                    lesson="",
                )

            if status == STATUS_LOCKED:
                decision.review_date = (now - timedelta(days=1)).date()
                decision.save(update_fields=["review_date", "modified_at"])
                create_review_due_notification(decision)

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {len(SEED_DECISIONS)} decisions, {len(DEMO_NOTES)} notes and a profile "
                f"for {DEMO_EMAIL} / {DEMO_PASSWORD}"
            )
        )
