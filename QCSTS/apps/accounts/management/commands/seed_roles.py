from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from apps.accounts.models import Role
from constants.permissions import PermissionCodes

class Command(BaseCommand):
    help = 'Seeds the database with dynamic Roles and Permissions.'

    def handle(self, *args, **options):
        self.stdout.write("Starting Role seeding...")

        permission_objects = {}
        for perm_code in PermissionCodes.ALL:
            try:
                perm = Permission.objects.get(codename=perm_code)
                permission_objects[perm_code] = perm
            except Permission.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"Warning: Permission '{perm_code}' not found. Run migrations first!"))

        roles_config = [
            {
                "name": "Admin",
                "description": "Full system access. Can manage users and all settings.",
                "perms": PermissionCodes.ALL
            },
            {
                "name": "QA Manager",
                "description": "Approves monographs, views audit trails, exports reports.",
                "perms": [
                    PermissionCodes.CAN_APPROVE_MONOGRAPH,
                    PermissionCodes.CAN_VIEW_AUDIT_TRAIL,
                    PermissionCodes.CAN_EXPORT_REPORT,
                    PermissionCodes.CAN_COUNTERSIGN_RESULT,
                ]
            },
            {
                "name": "Supervisor",
                "description": "Oversees stability batches and countersigns results.",
                "perms": [
                    PermissionCodes.CAN_CREATE_BATCH,
                    PermissionCodes.CAN_COUNTERSIGN_RESULT,
                    PermissionCodes.CAN_MANAGE_CHAMBER,
                ]
            },
            {
                "name": "Analyst",
                "description": "Submits routine stability tests and records sample pulls.",
                "perms": [
                    PermissionCodes.CAN_SUBMIT_RESULT,
                    PermissionCodes.CAN_MANAGE_CHAMBER,
                ]
            },
            {
                "name": "System User",
                "description": "Automated background tasks, API integrations, and Celery workers.",
                "perms": [
                    PermissionCodes.CAN_CREATE_BATCH,
                    PermissionCodes.CAN_SUBMIT_RESULT,
                ]
            }
        ]

        for config in roles_config:
            role, created = Role.objects.get_or_create(name=config["name"])
            role.description = config["description"]
            perm_list = [permission_objects[code] for code in config["perms"] if code in permission_objects]
            role.permissions.set(perm_list)
            role.save()
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created Role: {role.name}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"Updated Role: {role.name}"))

        self.stdout.write(self.style.SUCCESS("✅ Role seeding complete!"))