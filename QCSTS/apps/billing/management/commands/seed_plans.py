from decimal import Decimal

from django.core.management.base import BaseCommand

from apps.billing.models import Plan


class Command(BaseCommand):
    help = "Create or update the standard QCSTS SaaS plans."

    PLANS = [
        {
            "code": Plan.Code.ESSENTIAL,
            "name": "Essential",
            "description": "Single-site stability management for small pharmaceutical operations.",
            "monthly_price": Decimal("399.00"),
            "annual_price": Decimal("3990.00"),
            "max_users": 15,
            "max_sites": 1,
            "max_studies": 100,
            "max_storage_mb": 10240,
            "api_access": False,
        },
        {
            "code": Plan.Code.PROFESSIONAL,
            "name": "Professional",
            "description": "Multi-site stability operations with integrations and advanced quality workflows.",
            "monthly_price": Decimal("899.00"),
            "annual_price": Decimal("8990.00"),
            "max_users": 50,
            "max_sites": 3,
            "max_studies": 1000,
            "max_storage_mb": 102400,
            "api_access": True,
        },
        {
            "code": Plan.Code.ENTERPRISE,
            "name": "Enterprise",
            "description": "Custom multi-site deployment, validation, integrations and enterprise support.",
            "monthly_price": Decimal("2000.00"),
            "annual_price": Decimal("24000.00"),
            "max_users": None,
            "max_sites": None,
            "max_studies": None,
            "max_storage_mb": None,
            "api_access": True,
        },
    ]

    def handle(self, *args, **options):
        for payload in self.PLANS:
            code = payload.pop("code")
            plan, created = Plan.objects.update_or_create(code=code, defaults=payload)
            action = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(f"{action} plan: {plan.name}"))
