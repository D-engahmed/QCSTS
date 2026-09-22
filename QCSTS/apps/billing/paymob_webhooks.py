from decimal import Decimal

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from drf_spectacular.types import OpenApiTypes
from core.views import TenantExemptAPIView

from .models import Invoice, PaymentEvent, Subscription
from .paymob import verify_transaction_hmac


class PaymobTransactionWebhookView(TenantExemptAPIView):
    """Authenticated Paymob server-to-server transaction callback.

    The customer redirect is never treated as proof of payment. Paymob's
    transaction callback is the source of truth and must pass HMAC validation.
    """

    authentication_classes = []
    permission_classes = [AllowAny]

    @transaction.atomic
    @extend_schema(operation_id="paymob_transaction_webhook", request=OpenApiTypes.OBJECT, responses=OpenApiTypes.OBJECT)
    def post(self, request):
        obj = request.data.get("obj") if isinstance(request.data, dict) else None
        if not isinstance(obj, dict):
            return Response({"detail": "Invalid Paymob payload."}, status=400)

        supplied_hmac = request.query_params.get("hmac") or request.data.get("hmac")
        if not verify_transaction_hmac(obj, supplied_hmac, getattr(settings, "PAYMOB_HMAC_SECRET", "")):
            return Response({"detail": "Invalid callback signature."}, status=403)

        transaction_id = str(obj.get("id", "")).strip()
        order = obj.get("order")
        if not isinstance(order, dict):
            return Response({"detail": "Invalid Paymob order payload."}, status=400)
        source_data = obj.get("source_data")
        if source_data is not None and not isinstance(source_data, dict):
            return Response({"detail": "Invalid Paymob source_data payload."}, status=400)
        order_id = str(order.get("id", "")).strip()
        if not transaction_id or not order_id:
            return Response({"detail": "Missing transaction/order identifier."}, status=400)

        invoice = (
            Invoice.objects.select_for_update()
            .select_related("subscription", "organization")
            .filter(provider_order_id=order_id)
            .first()
        )
        if invoice is None:
            # Store no untrusted organization association. A later reconciliation
            # job can inspect the provider event after an invoice is created.
            return Response({"detail": "Unknown Paymob order."}, status=404)

        event, created = PaymentEvent.objects.select_for_update().get_or_create(
            provider="paymob",
            event_id=transaction_id,
            defaults={
                "organization": invoice.organization,
                "event_type": "transaction",
                "payload": request.data,
            },
        )
        if not created and event.processed:
            return Response({"status": "already_processed"}, status=200)

        try:
            amount_cents = int(obj.get("amount_cents") or 0)
        except (TypeError, ValueError):
            return Response({"detail": "Invalid amount_cents value."}, status=400)
        expected_cents = int((invoice.total * Decimal("100")).quantize(Decimal("1")))
        if amount_cents != expected_cents:
            return Response({"detail": "Payment amount does not match invoice."}, status=409)

        if str(obj.get("currency") or "").upper() != invoice.currency.upper():
            return Response({"detail": "Payment currency does not match invoice."}, status=409)

        event.payload = request.data
        event.event_type = "transaction"
        event.processed = True
        event.processed_at = timezone.now()
        event.save(update_fields=["payload", "event_type", "processed", "processed_at"])

        invoice.provider_transaction_id = transaction_id
        invoice.save(update_fields=["provider_transaction_id"])

        if bool(obj.get("success")) and not obj.get("is_refunded") and not obj.get("is_voided"):
            invoice.status = Invoice.Status.PAID
            invoice.paid_at = timezone.now()
            invoice.save(update_fields=["status", "paid_at"])

            subscription = invoice.subscription
            subscription.status = Subscription.Status.ACTIVE
            subscription.current_period_start = subscription.current_period_start or timezone.now()
            subscription.current_period_end = invoice.due_at
            subscription.save(update_fields=["status", "current_period_start", "current_period_end", "updated_at"])
        else:
            invoice.status = Invoice.Status.UNCOLLECTIBLE
            invoice.save(update_fields=["status"])

        return Response({"status": "processed"}, status=200)
