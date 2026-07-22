from django.urls import path
from apps.results.views import VerifySignatureView, SubmitResultView

urlpatterns = [
    path("signature/verify/", VerifySignatureView.as_view(), name="verify-signature"),
    path("", SubmitResultView.as_view(), name="submit-result"),
]