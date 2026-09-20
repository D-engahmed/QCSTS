from django.core.management.base import BaseCommand

from apps.platform.models import Permission, Role
from constants.permissions import PermissionCodes


class Command(BaseCommand):
    help = "Seeds the database with QCSTS organization-scoped system roles and permissions."

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
                "perms": PermissionCodes.ALL,
            },
            {
                "name": "qa_manager",
                "description": "Quality assurance management and approval.",
                "perms": [
                    PermissionCodes.CAN_APPROVE_MONOGRAPH,
                    PermissionCodes.CAN_VIEW_AUDIT_TRAIL,
                    PermissionCodes.CAN_EXPORT_REPORT,
                    PermissionCodes.CAN_COUNTERSIGN_RESULT,
                ],
            },
            {
                "name": "supervisor",
                "description": "Supervises stability execution and review.",
                "perms": [
                    PermissionCodes.CAN_CREATE_BATCH,
                    PermissionCodes.CAN_COUNTERSIGN_RESULT,
                    PermissionCodes.CAN_MANAGE_CHAMBER,
                ],
            },
            {
                "name": "analyst",
                "description": "Performs routine stability execution and result entry.",
                "perms": [
                    PermissionCodes.CAN_SUBMIT_RESULT,
                    PermissionCodes.CAN_MANAGE_CHAMBER,
                ],
            },
            {
                "name": "system",
                "description": "Automated background tasks and integrations.",
                "perms": [
                    PermissionCodes.CAN_CREATE_BATCH,
                    PermissionCodes.CAN_SUBMIT_RESULT,
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
                [
                    permission_objects[code]
                    for code in config["perms"]
                    if code in permission_objects
                ]
            )
            self.stdout.write(self.style.SUCCESS(f"Updated role: {role.name}"))

        self.stdout.write(self.style.SUCCESS("Role seeding complete."))
