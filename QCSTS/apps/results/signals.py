from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.results.models import TestResult

@receiver(post_save, sender=TestResult)
def update_test_point_status(sender, instance, **kwargs):
    """After a result is saved, update the related test point status."""
    instance.test_point.update_status()