from core.views import TenantScopedAPIView
from rest_framework import status
from drf_spectacular.utils import extend_schema
from django.utils import timezone

from apps.products.models import Monograph, MonographTest, Product
from apps.compliance.models import ElectronicSignature
from services.signature_service import SignatureService
from apps.products.serializers import (
    MonographSerializer,
    MonographCreateSerializer,
    MonographTestSerializer,
    ProductSerializer,
)
from core.permissions import IsAnalystOrAbove, IsQAManager
from core.responses import success_response, error_response
from core.exceptions import MonographAlreadyApproved
from services.audit_service import AuditService


class MonographListCreateView(TenantScopedAPIView):
    serializer_class = MonographSerializer
    permission_classes = [IsAnalystOrAbove]

    @extend_schema(operation_id="monograph_list")
    def get(self, request):
        queryset = self.tenant_qs(Monograph.objects.select_related("created_by", "approved_by"))
        return success_response(data=MonographSerializer(queryset, many=True).data)

    def post(self, request):
        serializer = MonographCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        monograph = serializer.save(created_by=request.user, organization=request.organization)

        AuditService.log(
            performed_by=request.user,
            action="CREATE",
            model_name="Monograph",
            object_id=monograph.id,
            object_repr=str(monograph),
            new_value=serializer.data,
            ip_address=request.META.get("REMOTE_ADDR"),
        )
        return success_response(
            data=MonographSerializer(monograph).data, status_code=status.HTTP_201_CREATED
        )


class MonographDetailView(TenantScopedAPIView):
    serializer_class = MonographSerializer
    permission_classes = [IsAnalystOrAbove]

    def get_object(self, request, pk):
        try:
            return self.tenant_qs(Monograph.objects.select_related("created_by", "approved_by")).get(pk=pk)
        except Monograph.DoesNotExist:
            return None

    @extend_schema(operation_id="monograph_retrieve")
    def get(self, request, pk):
        monograph = self.get_object(request, pk)
        if not monograph:
            return error_response({"detail": "Monograph not found."}, status.HTTP_404_NOT_FOUND)
        return success_response(data=MonographSerializer(monograph).data)

    def patch(self, request, pk):
        monograph = self.get_object(request, pk)
        if not monograph:
            return error_response({"detail": "Monograph not found."}, status.HTTP_404_NOT_FOUND)
        if monograph.is_approved():
            raise MonographAlreadyApproved()

        old_value = MonographSerializer(monograph).data
        serializer = MonographCreateSerializer(monograph, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        AuditService.log(
            performed_by=request.user,
            action="UPDATE",
            model_name="Monograph",
            object_id=monograph.id,
            object_repr=str(monograph),
            old_value=old_value,
            new_value=MonographSerializer(monograph).data,
            ip_address=request.META.get("REMOTE_ADDR"),
        )
        return success_response(data=MonographSerializer(monograph).data)


class MonographApproveView(TenantScopedAPIView):
    serializer_class = MonographSerializer
    permission_classes = [IsQAManager]

    def post(self, request, pk):
        try:
            monograph = self.tenant_qs(Monograph.objects.select_related("created_by", "approved_by")).get(pk=pk)
        except Monograph.DoesNotExist:
            return error_response({"detail": "Monograph not found."}, status.HTTP_404_NOT_FOUND)

        if monograph.is_approved():
            raise MonographAlreadyApproved()

        token = request.headers.get("X-Signature-Token")
        if not token or not SignatureService.validate(request.user, token):
            return error_response("Valid electronic signature authentication is required.", status_code=403)
        reason = request.data.get("reason", "").strip()
        if not reason:
            return error_response("Approval reason is required.", status_code=400)

        old_value = {"status": monograph.status}
        monograph.status = "approved"
        monograph.approved_by = request.user
        monograph.approved_at = timezone.now()
        monograph.save()

        signature = ElectronicSignature.issue(
            organization=request.organization,
            signer=request.user,
            record_type="Monograph",
            record_id=monograph.id,
            record_version=str(monograph.version),
            meaning=ElectronicSignature.Meaning.APPROVAL,
            reason=reason,
            authentication_secret=__import__("django.conf", fromlist=["settings"]).settings.SECRET_KEY,
        )

        AuditService.log(
            performed_by=request.user,
            action="APPROVE",
            model_name="Monograph",
            object_id=monograph.id,
            object_repr=str(monograph),
            old_value=old_value,
            new_value={"status": "approved", "signature_id": str(signature.id)},
            ip_address=request.META.get("REMOTE_ADDR"),
            organization=request.organization,
        )
        return success_response(
            data=MonographSerializer(monograph).data, message="Monograph approved successfully."
        )


class MonographTestListCreateView(TenantScopedAPIView):
    serializer_class = MonographTestSerializer
    permission_classes = [IsAnalystOrAbove]

    def get_monograph(self, request, pk):
        try:
            return self.tenant_qs(Monograph.objects.select_related("created_by", "approved_by")).get(pk=pk)
        except Monograph.DoesNotExist:
            return None

    def get(self, request, pk):
        monograph = self.get_monograph(request, pk)
        if not monograph:
            return error_response({"detail": "Monograph not found."}, status.HTTP_404_NOT_FOUND)
        tests = monograph.tests.all()
        return success_response(data=MonographTestSerializer(tests, many=True).data)

    def post(self, request, pk):
        monograph = self.get_monograph(request, pk)
        if not monograph:
            return error_response({"detail": "Monograph not found."}, status.HTTP_404_NOT_FOUND)
        if monograph.is_approved():
            raise MonographAlreadyApproved()

        serializer = MonographTestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        test = serializer.save(monograph=monograph, created_by=request.user, organization=request.organization)

        AuditService.log(
            performed_by=request.user,
            action="CREATE",
            model_name="MonographTest",
            object_id=test.id,
            object_repr=str(test),
            new_value=serializer.data,
            ip_address=request.META.get("REMOTE_ADDR"),
        )
        return success_response(
            data=MonographTestSerializer(test).data, status_code=status.HTTP_201_CREATED
        )


class ProductListCreateView(TenantScopedAPIView):
    serializer_class = ProductSerializer
    # Allow all authenticated users (analyst, supervisor, qa_manager, admin)
    permission_classes = [IsAnalystOrAbove]

    @extend_schema(operation_id="product_list")
    def get(self, request):
        queryset = self.tenant_qs(Product.objects.select_related("monograph", "created_by"))
        return success_response(data=ProductSerializer(queryset, many=True).data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        product = serializer.save(created_by=request.user, organization=request.organization)

        AuditService.log(
            performed_by=request.user,
            action="CREATE",
            model_name="Product",
            object_id=product.id,
            object_repr=str(product),
            new_value=serializer.data,
            ip_address=request.META.get("REMOTE_ADDR"),
        )
        return success_response(
            data=ProductSerializer(product).data, status_code=status.HTTP_201_CREATED
        )


class ProductDetailView(TenantScopedAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAnalystOrAbove]

    def get_object(self, request, pk):
        try:
            return self.tenant_qs(Product.objects.select_related("monograph", "created_by")).get(pk=pk)
        except Product.DoesNotExist:
            return None

    @extend_schema(operation_id="product_retrieve")
    def get(self, request, pk):
        product = self.get_object(request, pk)
        if not product:
            return error_response({"detail": "Product not found."}, status.HTTP_404_NOT_FOUND)
        return success_response(data=ProductSerializer(product).data)

    def patch(self, request, pk):
        product = self.get_object(request, pk)
        if not product:
            return error_response({"detail": "Product not found."}, status.HTTP_404_NOT_FOUND)
        old_value = ProductSerializer(product).data
        serializer = ProductSerializer(product, data=request.data, partial=True, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        AuditService.log(
            performed_by=request.user,
            action="UPDATE",
            model_name="Product",
            object_id=product.id,
            object_repr=str(product),
            old_value=old_value,
            new_value=ProductSerializer(product).data,
            ip_address=request.META.get("REMOTE_ADDR"),
        )
        return success_response(data=ProductSerializer(product).data)