from django.urls import path
from apps.results.views import (
    VerifySignatureView,
    SubmitResultView,
    SupervisorReviewResultView,
    QAApproveResultView,
    QARejectResultView,
)

urlpatterns = [
    path("signature/verify/", VerifySignatureView.as_view(), name="verify-signature"),
    path("<uuid:result_id>/review/", SupervisorReviewResultView.as_view(), name="review-result"),
    path("<uuid:result_id>/approve/", QAApproveResultView.as_view(), name="approve-result"),
    path("<uuid:result_id>/reject/", QARejectResultView.as_view(), name="reject-result"),
    path("", SubmitResultView.as_view(), name="submit-result"),
]