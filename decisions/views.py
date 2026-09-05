from django.core.paginator import Paginator
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from decisions.constants import (
    CHALLENGE_PENDING,
    CHALLENGE_READY,
    DEFAULT_PAGE_SIZE,
    STATUS_DRAFT,
    STATUS_LOCKED,
    STATUS_REVIEWED,
)
from decisions.errors import (
    CHALLENGE_ALREADY_REQUESTED,
    CHALLENGE_NOT_READY,
    DECISION_ALREADY_REVIEWED,
    DECISION_LOCKED,
    DECISION_NOT_FOUND,
    DECISION_NOT_LOCKED,
    NOTIFICATION_NOT_FOUND,
    REVIEW_DATE_IN_PAST,
)
from decisions.models import Challenge, Decision, Notification, Review
from decisions.serializers import (
    ConfidenceRevisionSerializer,
    DecisionSerializer,
    DecisionWriteSerializer,
    NotificationSerializer,
    ReviewSerializer,
    ReviewWriteSerializer,
)
from decisions.tasks import generate_challenge
from reckon.utils import get_paginated_response_dict


class DecisionViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    def get_decision(self, request, decision_uuid):
        return Decision.objects.filter(uuid=decision_uuid, user=request.user, is_deleted=False).first()

    def list(self, request):
        queryset = Decision.objects.filter(user=request.user, is_deleted=False).select_related("challenge", "review")

        status_filter = request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        category_filter = request.query_params.get("category")
        if category_filter:
            queryset = queryset.filter(category=category_filter)

        paginator = Paginator(queryset, DEFAULT_PAGE_SIZE)
        page_number = request.query_params.get("page", 1)
        page = paginator.get_page(page_number)
        results = DecisionSerializer(page.object_list, many=True).data
        return Response(get_paginated_response_dict(paginator, page.number, results))

    def retrieve(self, request, decision_uuid):
        decision = self.get_decision(request, decision_uuid)
        if not decision:
            return DECISION_NOT_FOUND.response()
        return Response(DecisionSerializer(decision).data)

    def create(self, request):
        serializer = DecisionWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if data["review_date"] <= timezone.localdate():
            return REVIEW_DATE_IN_PAST.response(details={"review_date": str(data["review_date"])})

        decision = Decision.objects.create(user=request.user, **data)
        return Response(DecisionSerializer(decision).data, status=201)

    def update(self, request, decision_uuid):
        decision = self.get_decision(request, decision_uuid)
        if not decision:
            return DECISION_NOT_FOUND.response()
        if decision.status != STATUS_DRAFT:
            return DECISION_LOCKED.response()

        serializer = DecisionWriteSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        for field, value in serializer.validated_data.items():
            setattr(decision, field, value)
        decision.save()
        return Response(DecisionSerializer(decision).data)

    def destroy(self, request, decision_uuid):
        decision = self.get_decision(request, decision_uuid)
        if not decision:
            return DECISION_NOT_FOUND.response()

        decision.is_deleted = True
        decision.save(update_fields=["is_deleted", "modified_at"])
        return Response(status=204)

    def challenge(self, request, decision_uuid):
        """Kicks off the devil's advocate. Heavy work goes to Celery, not this thread."""
        decision = self.get_decision(request, decision_uuid)
        if not decision:
            return DECISION_NOT_FOUND.response()
        if decision.status != STATUS_DRAFT:
            return DECISION_LOCKED.response()
        if Challenge.objects.filter(decision=decision).exists():
            return CHALLENGE_ALREADY_REQUESTED.response()

        Challenge.objects.create(decision=decision, status=CHALLENGE_PENDING)
        generate_challenge.delay(str(decision.uuid))
        return Response({"status": CHALLENGE_PENDING}, status=202)

    def revise_confidence(self, request, decision_uuid):
        """The one edit allowed after being challenged, and only before locking."""
        decision = self.get_decision(request, decision_uuid)
        if not decision:
            return DECISION_NOT_FOUND.response()
        if decision.status != STATUS_DRAFT:
            return DECISION_LOCKED.response()

        challenge = Challenge.objects.filter(decision=decision, status=CHALLENGE_READY).first()
        if not challenge:
            return CHALLENGE_NOT_READY.response()

        serializer = ConfidenceRevisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        decision.final_confidence = serializer.validated_data["final_confidence"]
        decision.save(update_fields=["final_confidence", "modified_at"])
        return Response(DecisionSerializer(decision).data)

    def lock(self, request, decision_uuid):
        """Freezes the decision. Nothing about it can change after this."""
        decision = self.get_decision(request, decision_uuid)
        if not decision:
            return DECISION_NOT_FOUND.response()
        if decision.status != STATUS_DRAFT:
            return DECISION_LOCKED.response()

        if decision.final_confidence is None:
            decision.final_confidence = decision.initial_confidence
        decision.status = STATUS_LOCKED
        decision.locked_at = timezone.now()
        decision.save(update_fields=["status", "locked_at", "final_confidence", "modified_at"])
        return Response(DecisionSerializer(decision).data)

    def review(self, request, decision_uuid):
        decision = self.get_decision(request, decision_uuid)
        if not decision:
            return DECISION_NOT_FOUND.response()
        if decision.status == STATUS_DRAFT:
            return DECISION_NOT_LOCKED.response()
        if decision.status == STATUS_REVIEWED:
            return DECISION_ALREADY_REVIEWED.response()

        serializer = ReviewWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        review = Review.objects.create(decision=decision, **serializer.validated_data)
        decision.status = STATUS_REVIEWED
        decision.save(update_fields=["status", "modified_at"])
        return Response(ReviewSerializer(review).data, status=201)


class NotificationViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        queryset = Notification.objects.filter(user=request.user, is_deleted=False)
        if request.query_params.get("unread") == "true":
            queryset = queryset.filter(read_at__isnull=True)
        return Response(NotificationSerializer(queryset[:50], many=True).data)

    def mark_read(self, request, notification_uuid):
        notification = Notification.objects.filter(uuid=notification_uuid, user=request.user, is_deleted=False).first()
        if not notification:
            return NOTIFICATION_NOT_FOUND.response()

        notification.read_at = timezone.now()
        notification.save(update_fields=["read_at", "modified_at"])
        return Response(NotificationSerializer(notification).data)
