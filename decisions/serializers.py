from rest_framework import serializers

from decisions.constants import CATEGORY_CHOICES, OUTCOME_CHOICES
from decisions.models import Challenge, Decision, Notification, Review


class ChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = [
            "status",
            "counterarguments",
            "blind_spots",
            "failure_conditions",
            "sharpest_question",
            "provider",
            "created_at",
        ]


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["uuid", "outcome", "what_happened", "lesson", "reviewed_at"]


class DecisionSerializer(serializers.ModelSerializer):
    challenge = ChallengeSerializer(read_only=True)
    review = ReviewSerializer(read_only=True)
    scored_confidence = serializers.IntegerField(read_only=True)
    confidence_shift = serializers.SerializerMethodField()

    class Meta:
        model = Decision
        fields = [
            "uuid",
            "title",
            "context",
            "options_considered",
            "chosen_option",
            "expected_outcome",
            "category",
            "initial_confidence",
            "final_confidence",
            "scored_confidence",
            "confidence_shift",
            "review_date",
            "status",
            "locked_at",
            "created_at",
            "challenge",
            "review",
        ]

    def get_confidence_shift(self, obj):
        """How many points the AI's argument moved them. None if never challenged."""
        if obj.final_confidence is None:
            return None
        return obj.final_confidence - obj.initial_confidence


class DecisionWriteSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    context = serializers.CharField()
    options_considered = serializers.ListField(child=serializers.CharField(max_length=300), required=False)
    chosen_option = serializers.CharField(max_length=300)
    expected_outcome = serializers.CharField()
    category = serializers.ChoiceField(choices=CATEGORY_CHOICES)
    initial_confidence = serializers.IntegerField(min_value=0, max_value=100)
    review_date = serializers.DateField()


class ConfidenceRevisionSerializer(serializers.Serializer):
    final_confidence = serializers.IntegerField(min_value=0, max_value=100)


class ReviewWriteSerializer(serializers.Serializer):
    outcome = serializers.ChoiceField(choices=OUTCOME_CHOICES)
    what_happened = serializers.CharField()
    lesson = serializers.CharField(required=False, allow_blank=True)


class NotificationSerializer(serializers.ModelSerializer):
    decision_uuid = serializers.UUIDField(source="decision.uuid", read_only=True)

    class Meta:
        model = Notification
        fields = ["uuid", "kind", "title", "body", "read_at", "created_at", "decision_uuid"]
