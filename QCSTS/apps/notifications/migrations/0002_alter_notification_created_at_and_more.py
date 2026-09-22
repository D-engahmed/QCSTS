import uuid

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Align the Notification schema with the current BaseModel field metadata.

    This migration intentionally preserves the existing database shape while
    synchronizing Django's historical migration state with the model definition.
    """

    dependencies = [
        ("notifications", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notification",
            name="id",
            field=models.UUIDField(
                default=uuid.uuid4,
                editable=False,
                help_text="Unique identifier for this record. Auto-generated UUID.",
                primary_key=True,
                serialize=False,
            ),
        ),
        migrations.AlterField(
            model_name="notification",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True,
                help_text="Timestamp when the record was created. Set by server, never editable.",
            ),
        ),
        migrations.AlterField(
            model_name="notification",
            name="updated_at",
            field=models.DateTimeField(
                auto_now=True,
                help_text="Timestamp of last modification. Updated automatically on every save.",
            ),
        ),
        migrations.AlterField(
            model_name="notification",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                help_text="The user who created this record.",
                null=True,
                on_delete=models.deletion.SET_NULL,
                related_name="%(app_label)s_%(class)s_created",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="notification",
            name="is_active",
            field=models.BooleanField(
                db_index=True,
                default=True,
                help_text="Soft delete flag. False means logically deleted. Record is never hard-deleted.",
            ),
        ),
        migrations.AlterField(
            model_name="notification",
            name="organization",
            field=models.ForeignKey(
                blank=True,
                db_index=True,
                null=True,
                on_delete=models.deletion.PROTECT,
                related_name="%(app_label)s_%(class)s_records",
                to="platform.organization",
            ),
        ),
    ]
