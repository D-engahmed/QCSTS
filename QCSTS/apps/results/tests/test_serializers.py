import pytest
from apps.results.serializers import TestResultSerializer
from apps.products.tests.factories import MonographTestFactory, MonographFactory
from apps.batches.tests.factories import BatchFactory
from apps.platform.models import Organization
from apps.schedule.models import TestPoint

@pytest.mark.django_db
class TestTestResultSerializerTenantIsolation:
    def test_cannot_submit_result_for_other_tenants_test_point(self):
        # Create two separate organizations (tenants)
        org_a = Organization.objects.create(name="Org A", slug="org-a")
        org_b = Organization.objects.create(name="Org B", slug="org-b")
        
        # Create a batch for Tenant B. 
        # The post_save signal (ScheduleEngine) automatically creates TestPoints for this batch.
        batch_b = BatchFactory(organization=org_b)
        
        # Fetch the auto-created TestPoint instead of creating a new one to avoid UNIQUE constraint errors
        tp_b = TestPoint.objects.filter(batch=batch_b).first()
        
        # Create a valid monograph test for Tenant A
        monograph_a = MonographFactory(organization=org_a)
        mt_a = MonographTestFactory(monograph=monograph_a)

        # Simulate a request from Tenant A
        request = type('Request', (object,), {'organization': org_a})()
        
        serializer = TestResultSerializer(
            data={
                "test_point": tp_b.id,
                "monograph_test": mt_a.id,
                "value": "99.5",
                "unit": "%"
            },
            context={"request": request}
        )
        
        assert not serializer.is_valid()
        # The test_point must be invalid because it belongs to org_b
        assert "test_point" in serializer.errors

@pytest.mark.django_db
class TestTestResultImmutability:
    def test_soft_deleted_result_cannot_be_modified(self):
        from apps.results.tests.factories import TestResultFactory
        
        result = TestResultFactory()
        
        # This should now succeed because we allowed is_active/updated_at updates
        result.soft_delete() 
        assert result.is_active is False
        
        # But trying to change actual data must still fail
        result.value = "50.0"
        with pytest.raises(PermissionError):
            result.save() # Should fail because of the all_objects check