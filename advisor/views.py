from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from advisor.constants import HISTORY_LIMIT, ROLE_ASSISTANT, ROLE_USER, TOPIC_MONEY
from advisor.errors import PROFILE_REQUIRED_FOR_MONEY
from advisor.models import AdvisorMessage
from advisor.serializers import AdvisorMessageSerializer, AskSerializer
from advisor.utils import classify_topic, parse_amount
from reckon.ai import get_provider
from insights.utils import build_track_record
from profiles.models import Profile
from profiles.utils import assess_purchase, build_profile_context


class AdvisorView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        messages = AdvisorMessage.objects.filter(user=request.user, is_deleted=False)[:HISTORY_LIMIT]
        return Response(AdvisorMessageSerializer(messages, many=True).data)

    def post(self, request):
        serializer = AskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        question = serializer.validated_data["question"]

        topic = classify_topic(question)
        profile, _ = Profile.objects.get_or_create(user=request.user)

        if topic == TOPIC_MONEY and not profile.is_complete:
            return PROFILE_REQUIRED_FOR_MONEY.response()

        # The arithmetic is computed here, from their own figures, and handed to
        # the provider. No model ever invents a number.
        amount = serializer.validated_data.get("amount") or parse_amount(question)
        assessment = assess_purchase(profile, amount) if topic == TOPIC_MONEY and amount else None

        history = list(
            AdvisorMessage.objects.filter(user=request.user, is_deleted=False)
            .order_by("-created_at")[:HISTORY_LIMIT]
            .values("role", "content")
        )
        history.reverse()

        AdvisorMessage.objects.create(user=request.user, role=ROLE_USER, content=question, topic=topic)

        provider = get_provider()
        result = provider.advise(
            question=question,
            topic=topic,
            profile=build_profile_context(profile),
            track_record=build_track_record(request.user),
            assessment=assessment,
            history=history,
        )

        message = AdvisorMessage.objects.create(
            user=request.user,
            role=ROLE_ASSISTANT,
            content=result["answer"],
            topic=topic,
            numbers=result.get("numbers") or [],
            considerations=result.get("considerations") or [],
            watch_outs=result.get("watch_outs") or [],
            suggested_decision=result.get("suggested_decision") or {},
            provider=provider.name,
        )
        return Response(AdvisorMessageSerializer(message).data, status=201)
