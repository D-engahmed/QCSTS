import pytest
from rest_framework.test import APIClient
from django.core.cache import cache
from apps.accounts.tests.factories import UserFactory
from apps.batches.tests.factories import BatchFactory
from apps.schedule.models import TestPoint
from apps.results.models import TestResult


def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def get_signature_token(user):
    """Helper — creates a valid signature token in Redis for a user."""
    import uuid

    token = str(uuid.uuid4())
    cache_key = f"sig_token:{user.id}:{token}"
    cache.set(cache_key, True, timeout=300)
    return token


@pytest.mark.django_db
class TestSignatureVerifyView:

    def test_valid_password_returns_token(self):
        analyst = UserFactory()
        c = auth_client(analyst)
        response = c.post("/api/v1/results/signature/verify/", {"password": "TestPass123!"})
        assert response.status_code == 200
        assert "signature_token" in response.data["data"]

    def test_wrong_password_fails(self):
        analyst = UserFactory()
        c = auth_client(analyst)
        response = c.post("/api/v1/results/signature/verify/", {"password": "WrongPassword!"})
        assert response.status_code == 401

    def test_missing_password_returns_400(self):
        analyst = UserFactory()
        c = auth_client(analyst)
        response = c.post("/api/v1/results/signature/verify/", {})
        assert response.status_code == 400


@pytest.mark.django_db
class TestTestResultSubmission:

    def test_analyst_can_submit_result_with_signature(self):
        analyst = UserFactory()
        batch = BatchFactory()
        tp = TestPoint.objects.filter(batch=batch).first()
        monograph_test = batch.product.monograph.tests.first()

        token = get_signature_token(analyst)
        c = auth_client(analyst)
        c.credentials(
            HTTP_AUTHORIZATION=f"Bearer {analyst.id}",
            HTTP_X_SIGNATURE_TOKEN=token,
        )
        c.force_authenticate(user=analyst)

        response = c.post(
            "/api/v1/results/",
            {
                "test_point": str(tp.id),
                "monograph_test": str(monograph_test.id),
                "value": "99.5",
                "unit": "%",
            },
            HTTP_X_SIGNATURE_TOKEN=token,
        )
        assert response.status_code == 201
        assert response.data["data"]["pass_fail"] in ["pass", "fail"]

    def test_cannot_submit_without_signature(self):
        analyst = UserFactory()
        batch = BatchFactory()
        tp = TestPoint.objects.filter(batch=batch).first()
        monograph_test = batch.product.monograph.tests.first()

        c = auth_client(analyst)
        response = c.post(
            "/api/v1/results/",
            {
                "test_point": str(tp.id),
                "monograph_test": str(monograph_test.id),
                "value": "99.5",
                "unit": "%",
            },
        )
        assert response.status_code == 403

    def test_cannot_submit_duplicate_result(self):
        analyst = UserFactory()
        batch = BatchFactory()
        tp = TestPoint.objects.filter(batch=batch).first()
        monograph_test = batch.product.monograph.tests.first()

        # Create first result directly
        TestResult.objects.create(
            test_point=tp,
            monograph_test=monograph_test,
            value="99.5",
            unit="%",
            specification_snapshot=monograph_test.specification,
            pass_fail="pass",
            analyst=analyst,
            created_by=analyst,
        )

        token = get_signature_token(analyst)
        c = auth_client(analyst)
        response = c.post(
            "/api/v1/results/",
            {
                "test_point": str(tp.id),
                "monograph_test": str(monograph_test.id),
                "value": "99.5",
                "unit": "%",
            },
            HTTP_X_SIGNATURE_TOKEN=token,
        )
        assert response.status_code in [400, 409]


@pytest.mark.django_db
class TestTestResultListView:

    def test_analyst_can_list_results(self):
        analyst = UserFactory()
        c = auth_client(analyst)
        response = c.get("/api/v1/results/")
        assert response.status_code == 200
        assert response.data["success"] is True

    def test_filter_by_test_point(self):
        analyst = UserFactory()
        batch = BatchFactory()
        tp = TestPoint.objects.filter(batch=batch).first()
        c = auth_client(analyst)
        response = c.get(f"/api/v1/results/?test_point={tp.id}")
        assert response.status_code == 200

    def test_filter_by_batch_returns_results_across_all_its_test_points(self):
        analyst = UserFactory()
        batch = BatchFactory()
        other_batch = BatchFactory()
        tp1, tp2 = TestPoint.objects.filter(batch=batch)[:2]
        other_tp = TestPoint.objects.filter(batch=other_batch).first()
        monograph_test = batch.product.monograph.tests.first()
        other_monograph_test = other_batch.product.monograph.tests.first()

        TestResult.objects.create(
            test_point=tp1, monograph_test=monograph_test, value="99.5",
            specification_snapshot=monograph_test.specification, pass_fail="pass",
            analyst=analyst, created_by=analyst,
        )
        TestResult.objects.create(
            test_point=tp2, monograph_test=monograph_test, value="101.0",
            specification_snapshot=monograph_test.specification, pass_fail="pass",
            analyst=analyst, created_by=analyst,
        )
        TestResult.objects.create(
            test_point=other_tp, monograph_test=other_monograph_test, value="50.0",
            specification_snapshot=other_monograph_test.specification, pass_fail="fail",
            analyst=analyst, created_by=analyst,
        )

        c = auth_client(analyst)
        response = c.get(f"/api/v1/results/?batch={batch.id}")
        assert response.status_code == 200
        returned_test_points = {str(r["test_point"]) for r in response.data["data"]}
        assert returned_test_points == {str(tp1.id), str(tp2.id)}

    def test_unauthenticated_cannot_list_results(self):
        client = APIClient()
        response = client.get("/api/v1/results/")
        assert response.status_code == 401


@pytest.mark.django_db
class TestOutcomeEvaluator:

    def test_pass_within_range(self):
        from services.outcome_evaluator import OutcomeEvaluator

        assert OutcomeEvaluator.evaluate("99.5", "98.0 - 102.0") == "pass"

    def test_fail_below_range(self):
        from services.outcome_evaluator import OutcomeEvaluator

        assert OutcomeEvaluator.evaluate("97.0", "98.0 - 102.0") == "fail"

    def test_fail_above_range(self):
        from services.outcome_evaluator import OutcomeEvaluator

        assert OutcomeEvaluator.evaluate("103.0", "98.0 - 102.0") == "fail"

    def test_nlt_pass(self):
        from services.outcome_evaluator import OutcomeEvaluator

        assert OutcomeEvaluator.evaluate("80", "NLT 75") == "pass"

    def test_nlt_fail(self):
        from services.outcome_evaluator import OutcomeEvaluator

        assert OutcomeEvaluator.evaluate("70", "NLT 75") == "fail"

    def test_nmt_pass(self):
        from services.outcome_evaluator import OutcomeEvaluator

        assert OutcomeEvaluator.evaluate("4.0", "NMT 5.0") == "pass"

    def test_nmt_fail(self):
        from services.outcome_evaluator import OutcomeEvaluator

        assert OutcomeEvaluator.evaluate("6.0", "NMT 5.0") == "fail"
