from django.core.management.base import BaseCommand

from apps.platform.models import Permission, Role


class Command(BaseCommand):
    help = "Seeds the database with QCSTS organization-scoped roles and permissions."

    def handle(self, *args, **options):
        self.stdout.write("Starting role seeding...")

        permission_objects = {
            permission.code: permission
            for permission in Permission.objects.all()
        }

        roles_config = [
            {
                "name": "admin",
                "description": "Organization administrator.",
                "perms": sorted(permission_objects),
            },
            {
                "name": "qa_manager",
                "description": "Quality assurance management and approval.",
                "perms": [
                    "audit.view",
                    "result.approve",
                    "result.review",
                    "report.export",
                ],
            },
            {
                "name": "supervisor",
                "description": "Supervises stability execution and review.",
                "perms": [
                    "batch.create",
                    "result.review",
                    "chamber.manage",
                ],
            },
            {
                "name": "analyst",
                "description": "Performs routine stability execution and result entry.",
                "perms": [
                    "result.submit",
                    "sample.manage",
                ],
            },
            {
                "name": "system",
                "description": "Automated background tasks and integrations.",
                "perms": [
                    "batch.create",
                    "result.submit",
                ],
            },
        ]

        for config in roles_config:
            role, _ = Role.objects.get_or_create(
                organization=None,
                name=config["name"],
                defaults={
                    "description": config["description"],
                    "is_system": True,
                },
            )
            role.description = config["description"]
            role.is_system = True
            role.save(update_fields=["description", "is_system"])
            role.permissions.set(
                [permission_objects[code] for code in config["perms"] if code in permission_objects]
            )
            self.stdout.write(self.style.SUCCESS(f"Updated role: {role.name}"))

        self.stdout.write(self.style.SUCCESS("Role seeding complete."))
