from django.db import migrations


class Migration(migrations.Migration):
    """
    Historical compatibility migration.

    The password_changed_at field was already present in accounts.0001_initial.
    The later 0004 migration attempted to add the same database column again,
    which made fresh database provisioning fail. Keep the migration node for
    already-recorded migration histories, but perform no database operation.
    """

    dependencies = [
        ("accounts", "0003_customuser_locked_until"),
    ]

    operations = []
