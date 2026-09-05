from decimal import Decimal

from rest_framework import serializers

from advisor.constants import MAX_QUESTION_LENGTH
from advisor.models import AdvisorMessage


class AdvisorMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdvisorMessage
        fields = [
            "uuid",
            "role",
            "content",
            "topic",
            "numbers",
            "considerations",
            "watch_outs",
            "suggested_decision",
            "provider",
            "created_at",
        ]


class AskSerializer(serializers.Serializer):
    question = serializers.CharField(max_length=MAX_QUESTION_LENGTH)
    # Optional override for when the parser guesses wrong, or the price is not
    # in the question at all.
    amount = serializers.DecimalField(max_digits=14, decimal_places=2, required=False, min_value=Decimal("0"))
