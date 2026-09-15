from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    initial = True
    dependencies = [("accounts", "0003_customuser_locked_until"), ("platform", "0001_initial")]
    operations = [
        migrations.CreateModel(name="ElectronicSignature", fields=[
            ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)), ("created_at", models.DateTimeField(auto_now_add=True)), ("updated_at", models.DateTimeField(auto_now=True)), ("is_active", models.BooleanField(default=True)),
            ("record_type", models.CharField(max_length=120)), ("record_id", models.UUIDField()), ("record_version", models.CharField(max_length=64)),
            ("meaning", models.CharField(choices=[("review","Review"),("approval","Approval"),("rejection","Rejection"),("release","Release"),("closure","Closure")], max_length=32)), ("reason", models.TextField()), ("signed_at", models.DateTimeField(auto_now_add=True)), ("authentication_fingerprint", models.CharField(max_length=128)), ("signature_digest", models.CharField(max_length=128, unique=True)),
            ("organization", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="electronic_signatures", to="platform.organization")), ("signer", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="electronic_signatures", to="accounts.customuser")),
        ], options={"db_table":"compliance_electronic_signature","ordering":["-signed_at"]}),
        migrations.CreateModel(name="ValidationArtifact", fields=[
            ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)), ("created_at", models.DateTimeField(auto_now_add=True)), ("updated_at", models.DateTimeField(auto_now=True)), ("is_active", models.BooleanField(default=True)),
            ("artifact_type", models.CharField(choices=[("urs","URS"),("frs","FRS"),("risk","Risk Assessment"),("traceability","Traceability Matrix"),("iq","IQ"),("oq","OQ"),("pq","PQ"),("summary","Validation Summary")], max_length=32)), ("version", models.CharField(max_length=64)), ("title", models.CharField(max_length=255)), ("content_hash", models.CharField(max_length=128)), ("approved", models.BooleanField(default=False)), ("approved_at", models.DateTimeField(blank=True, null=True)),
            ("organization", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="validation_artifacts", to="platform.organization")), ("approved_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="approved_validation_artifacts", to="accounts.customuser")),
        ], options={"db_table":"compliance_validation_artifact"}),
        migrations.AddConstraint(model_name="electronicsignature", constraint=models.UniqueConstraint(fields=("organization","record_type","record_id","record_version","meaning"), name="one_signature_per_record_meaning")),
        migrations.AddConstraint(model_name="validationartifact", constraint=models.UniqueConstraint(fields=("organization","artifact_type","version"), name="validation_artifact_version_unique")),
    ]
