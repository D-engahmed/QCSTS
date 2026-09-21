import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0005_email_verification"),
        ("platform", "0002_single_active_membership"),
    ]

    operations = [
        migrations.CreateModel(
            name="Notification",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("kind", models.CharField(choices=[("system","System"),("approval","Approval"),("overdue","Overdue"),("quality","Quality"),("billing","Billing")], default="system", max_length=20)),
                ("severity", models.CharField(choices=[("info","Info"),("warning","Warning"),("critical","Critical")], default="info", max_length=20)),
                ("title", models.CharField(max_length=255)),
                ("body", models.TextField()),
                ("action_url", models.CharField(blank=True, max_length=500)),
                ("read_at", models.DateTimeField(blank=True, null=True)),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="notifications_notification_created", to="accounts.customuser")),
                ("organization", models.ForeignKey(blank=True, db_index=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="notifications_notification_records", to="platform.organization")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="notifications", to="accounts.customuser")),
            ],
            options={"db_table":"notifications_notification","ordering":["-created_at"]},
        ),
        migrations.AddIndex(
            model_name="notification",
            index=models.Index(fields=["organization","user","read_at"], name="notificatio_organiz_1dd1e2_idx"),
        ),
        migrations.AddIndex(
            model_name="notification",
            index=models.Index(fields=["organization","kind"], name="notificatio_organiz_36f7bc_idx"),
        ),
    ]
