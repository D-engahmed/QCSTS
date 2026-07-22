from rest_framework.views import APIView
from rest_framework import status
from django.utils import timezone

from apps.products.models import Monograph, MonographTest, Product
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


class MonographListCreateView(APIView):
    serializer_class = MonographSerializer
    permission_classes = [IsAnalystOrAbove]

    def get(self, request):
        monographs = Monograph.objects.all()
        return success_response(data=MonographSerializer(monographs, many=True).data)

    def post(self, request):
        serializer = MonographCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        monograph = serializer.save(created_by=request.user)

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


class MonographDetailView(APIView):
    serializer_class = MonographSerializer
    permission_classes = [IsAnalystOrAbove]

    def get_object(self, pk):
        try:
            return Monograph.objects.get(pk=pk)
        except Monograph.DoesNotExist:
            return None

    def get(self, request, pk):
        monograph = self.get_object(pk)
        if not monograph:
            return error_response({"detail": "Monograph not found."}, status.HTTP_404_NOT_FOUND)
        return success_response(data=MonographSerializer(monograph).data)

    def patch(self, request, pk):
        monograph = self.get_object(pk)
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


class MonographApproveView(APIView):
    serializer_class = MonographSerializer
    permission_classes = [IsQAManager]

    def post(self, request, pk):
        try:
            monograph = Monograph.objects.get(pk=pk)
        except Monograph.DoesNotExist:
            return error_response({"detail": "Monograph not found."}, status.HTTP_404_NOT_FOUND)

        if monograph.is_approved():
            raise MonographAlreadyApproved()

        old_value = {"status": monograph.status}
        monograph.status = "approved"
        monograph.approved_by = request.user
        monograph.approved_at = timezone.now()
        monograph.save()

        AuditService.log(
            performed_by=request.user,
            action="APPROVE",
            model_name="Monograph",
            object_id=monograph.id,
            object_repr=str(monograph),
            old_value=old_value,
            new_value={"status": "approved"},
            ip_address=request.META.get("REMOTE_ADDR"),
        )
        return success_response(
            data=MonographSerializer(monograph).data, message="Monograph approved successfully."
        )


class MonographTestListCreateView(APIView):
    serializer_class = MonographTestSerializer
    permission_classes = [IsAnalystOrAbove]

    def get_monograph(self, pk):
        try:
            return Monograph.objects.get(pk=pk)
        except Monograph.DoesNotExist:
            return None

    def get(self, request, pk):
        monograph = self.get_monograph(pk)
        if not monograph:
            return error_response({"detail": "Monograph not found."}, status.HTTP_404_NOT_FOUND)
        tests = monograph.tests.all()
        return success_response(data=MonographTestSerializer(tests, many=True).data)

    def post(self, request, pk):
        monograph = self.get_monograph(pk)
        if not monograph:
            return error_response({"detail": "Monograph not found."}, status.HTTP_404_NOT_FOUND)
        if monograph.is_approved():
            raise MonographAlreadyApproved()

        serializer = MonographTestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        test = serializer.save(monograph=monograph, created_by=request.user)

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


class ProductListCreateView(APIView):
    serializer_class = ProductSerializer
    # Allow all authenticated users (analyst, supervisor, qa_manager, admin)
    permission_classes = [IsAnalystOrAbove]

    def get(self, request):
        products = Product.objects.all()
        # FIXED: added missing closing parenthesis
        return success_response(data=ProductSerializer(products, many=True).data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save(created_by=request.user)

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


class ProductDetailView(APIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAnalystOrAbove]

    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return None

    def get(self, request, pk):
        product = self.get_object(pk)
        if not product:
            return error_response({"detail": "Product not found."}, status.HTTP_404_NOT_FOUND)
        return success_response(data=ProductSerializer(product).data)

    def patch(self, request, pk):
        product = self.get_object(pk)
        if not product:
            return error_response({"detail": "Product not found."}, status.HTTP_404_NOT_FOUND)
        old_value = ProductSerializer(product).data
        serializer = ProductSerializer(product, data=request.data, partial=True)
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