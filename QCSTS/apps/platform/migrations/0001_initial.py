# Generated manually for the Phase 1 organization foundation.
import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name="Organization",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=255)),
                ("legal_name", models.CharField(blank=True, max_length=255)),
                ("slug", models.SlugField(max_length=80, unique=True)),
                ("country", models.CharField(max_length=2)),
                ("timezone", models.CharField(default="UTC", max_length=64)),
                ("currency", models.CharField(default="USD", max_length=3)),
                ("status", models.CharField(choices=[("active", "Active"), ("suspended", "Suspended"), ("archived", "Archived")], default="active", max_length=16)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ], options={"db_table": "platform_organization", "ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Permission",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("code", models.SlugField(max_length=100, unique=True)), ("name", models.CharField(max_length=120)),
                ("description", models.TextField(blank=True)), ("created_at", models.DateTimeField(auto_now_add=True)), ("updated_at", models.DateTimeField(auto_now=True)),
            ], options={"db_table": "platform_permission", "ordering": ["code"]},
        ),
        migrations.CreateModel(
            name="Site",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=255)), ("address", models.TextField(blank=True)),
                ("country", models.CharField(max_length=2)), ("timezone", models.CharField(default="UTC", max_length=64)),
                ("status", models.CharField(choices=[("active", "Active"), ("inactive", "Inactive")], default="active", max_length=16)),
                ("created_at", models.DateTimeField(auto_now_add=True)), ("updated_at", models.DateTimeField(auto_now=True)),
                ("organization", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="sites", to="platform.organization")),
            ], options={"db_table": "platform_site", "ordering": ["organization__name", "name"]},
        ),
        migrations.CreateModel(
            name="Role",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=120)), ("description", models.TextField(blank=True)),
                ("is_system", models.BooleanField(default=False)), ("created_at", models.DateTimeField(auto_now_add=True)), ("updated_at", models.DateTimeField(auto_now=True)),
                ("organization", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="roles", to="platform.organization")),
                ("permissions", models.ManyToManyField(blank=True, related_name="roles", to="platform.permission")),
            ], options={"db_table": "platform_role", "ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Membership",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)), ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)), ("updated_at", models.DateTimeField(auto_now=True)),
                ("default_site", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="default_for_memberships", to="platform.site")),
                ("organization", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="memberships", to="platform.organization")),
                ("role", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="memberships", to="platform.role")),
                ("sites", models.ManyToManyField(blank=True, related_name="memberships", to="platform.site")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="memberships", to=settings.AUTH_USER_MODEL)),
            ], options={"db_table": "platform_membership"},
        ),
        migrations.AddConstraint(model_name="site", constraint=models.UniqueConstraint(fields=("organization", "name"), name="site_name_per_org")),
        migrations.AddConstraint(model_name="role", constraint=models.UniqueConstraint(fields=("organization", "name"), name="role_name_per_org")),
        migrations.AddConstraint(model_name="membership", constraint=models.UniqueConstraint(fields=("user", "organization"), name="one_membership_per_org")),
        migrations.AddIndex(model_name="membership", index=models.Index(fields=["user", "is_active"], name="platform_me_user_id_68309a_idx")),
        migrations.AddIndex(model_name="membership", index=models.Index(fields=["organization", "is_active"], name="platform_me_organiz_d92476_idx")),
    ]
