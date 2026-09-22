from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from core.views import TenantScopedModelViewSet
from core.permissions import IsAnalystOrAbove
from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(TenantScopedModelViewSet):
    permission_classes = [IsAnalystOrAbove]
    serializer_class = NotificationSerializer
    queryset = Notification.objects.select_related("user")

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def get_permissions(self):
        return [IsAnalystOrAbove()]

    @action(detail=True, methods=["post"])
    def read(self, request, pk=None):
        notification = self.get_object()
        notification.read_at = timezone.now()
        notification.save(update_fields=["read_at", "updated_at"])
        return Response(self.get_serializer(notification).data)

    @action(detail=False, methods=["post"], url_path="read-all")
    def read_all(self, request):
        updated = self.get_queryset().filter(read_at__isnull=True).update(
            read_at=timezone.now(),
            updated_at=timezone.now(),
        )
        return Response({"updated": updated}, status=status.HTTP_200_OK)
