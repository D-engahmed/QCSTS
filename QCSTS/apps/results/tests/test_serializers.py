import pytest
from apps.results.serializers import TestResultSerializer
from apps.schedule.tests.factories import TestPointFactory
from apps.products.tests.factories import MonographTestFactory

@pytest.mark.django_db
class TestTestResultSerializerTenantIsolation:
    def test_cannot_submit_result_for_other_tenants_test_point(self, user, organization, other_organization):
        # Create a test point for ANOTHER tenant
        other_tp = TestPointFactory(batch__organization=other_organization)
        
        # Create a valid monograph test for current tenant
        valid_mt = MonographTestFactory(monograph__organization=organization)

        request = type('Request', (object,), {'organization': organization})()
        
        serializer = TestResultSerializer(
            data={
                "test_point": other_tp.id,
                "monograph_test": valid_mt.id,
                "value": "99.5",
                "unit": "%"
            },
            context={"request": request}
        )
        
        assert not serializer.is_valid()
        assert "test_point" in serializer.errors

@pytest.mark.django_db
class TestTestResultImmutability:
    def test_soft_deleted_result_cannot_be_modified(self):
        from apps.results.tests.factories import TestResultFactory
        
        result = TestResultFactory()
        result.soft_delete() # Marks as is_active=False
        
        result.value = "50.0"
        with pytest.raises(PermissionError):
            result.save() # Should still fail because of all_objects check