from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [("compliance", "0001_initial")]
    operations = [
        migrations.CreateModel(
            name="ControlledRecord",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)), ("created_at", models.DateTimeField(auto_now_add=True)), ("updated_at", models.DateTimeField(auto_now=True)), ("is_active", models.BooleanField(default=True)),
                ("record_type", models.CharField(max_length=120)), ("record_id", models.UUIDField()), ("version", models.PositiveIntegerField(default=1)),
                ("status", models.CharField(choices=[("draft","Draft"),("submitted","Submitted"),("under_review","Under review"),("approved","Approved"),("rejected","Rejected"),("locked","Locked"),("correction","Correction required")], default="draft", max_length=24)),
                ("locked_at", models.DateTimeField(blank=True, null=True)), ("approved_at", models.DateTimeField(blank=True, null=True)),
                ("organization", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="controlled_records", to="platform.organization")),
                ("approved_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="approved_records", to="accounts.customuser")),
                ("locked_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="locked_records", to="accounts.customuser")),
            ], options={"db_table":"compliance_controlled_record"},
        ),
        migrations.AddConstraint(model_name="controlledrecord", constraint=models.UniqueConstraint(fields=("organization","record_type","record_id"), name="controlled_record_unique")),
    ]
