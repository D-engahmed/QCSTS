from django.db import migrations, models
import django.db.models.deletion
import uuid


SEVERITY = [("low", "Low"), ("medium", "Medium"), ("high", "High"), ("critical", "Critical")]
STATUS = [("open", "Open"), ("investigation", "Investigation"), ("pending_approval", "Pending approval"), ("approved", "Approved"), ("closed", "Closed"), ("canceled", "Canceled")]


def common_fields():
    return [
        ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
        ("created_at", models.DateTimeField(auto_now_add=True)),
        ("updated_at", models.DateTimeField(auto_now=True)),
        ("is_active", models.BooleanField(default=True)),
        ("reference", models.CharField(max_length=64)), ("title", models.CharField(max_length=255)), ("description", models.TextField()),
        ("severity", models.CharField(choices=SEVERITY, default="medium", max_length=16)),
        ("status", models.CharField(choices=STATUS, default="open", max_length=24)),
        ("due_at", models.DateTimeField(blank=True, null=True)), ("root_cause", models.TextField(blank=True)), ("impact_assessment", models.TextField(blank=True)), ("closed_at", models.DateTimeField(blank=True, null=True)),
        ("organization", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="+", to="platform.organization")),
        ("owner", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="+", to="accounts.customuser")),
    ]


class Migration(migrations.Migration):
    initial = True
    dependencies = [("accounts", "0003_customuser_locked_until"), ("results", "0004_resultcorrection_and_more"), ("platform", "0001_initial")]
    operations = [
        migrations.CreateModel(name="OOSInvestigation", fields=common_fields()+[
            ("phase", models.CharField(default="phase_i", max_length=32)), ("laboratory_assessment", models.TextField(blank=True)), ("manufacturing_assessment", models.TextField(blank=True)), ("disposition", models.TextField(blank=True)),
            ("result", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="oos_investigations", to="results.testresult")),
        ], options={"db_table":"quality_oos_investigation","ordering":["-created_at"]}),
        migrations.CreateModel(name="OOTInvestigation", fields=common_fields()+[
            ("trend_description", models.TextField(blank=True)), ("statistical_assessment", models.TextField(blank=True)), ("disposition", models.TextField(blank=True)),
            ("result", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="oot_investigations", to="results.testresult")),
        ], options={"db_table":"quality_oot_investigation","ordering":["-created_at"]}),
        migrations.CreateModel(name="Deviation", fields=common_fields()+[
            ("detected_at", models.DateTimeField(blank=True, null=True)), ("process_area", models.CharField(blank=True, max_length=120)), ("immediate_action", models.TextField(blank=True)), ("risk_score", models.PositiveIntegerField(blank=True, null=True)),
        ], options={"db_table":"quality_deviation","ordering":["-created_at"]}),
        migrations.CreateModel(name="CAPA", fields=common_fields()+[
            ("corrective_action", models.TextField()), ("preventive_action", models.TextField(blank=True)), ("effectiveness_check", models.TextField(blank=True)), ("effectiveness_due_at", models.DateTimeField(blank=True, null=True)), ("effectiveness_verified_at", models.DateTimeField(blank=True, null=True)),
        ], options={"db_table":"quality_capa","ordering":["-created_at"]}),
        migrations.CreateModel(name="ChangeControl", fields=common_fields()+[
            ("change_type", models.CharField(max_length=120)), ("current_state", models.TextField()), ("proposed_state", models.TextField()), ("risk_assessment", models.TextField()), ("implementation_plan", models.TextField(blank=True)), ("implemented_at", models.DateTimeField(blank=True, null=True)),
        ], options={"db_table":"quality_change_control","ordering":["-created_at"]}),
        migrations.AddConstraint(model_name="oosinvestigation", constraint=models.UniqueConstraint(fields=("organization","reference"), name="oos_reference_per_org")),
        migrations.AddConstraint(model_name="ootinvestigation", constraint=models.UniqueConstraint(fields=("organization","reference"), name="oot_reference_per_org")),
        migrations.AddConstraint(model_name="deviation", constraint=models.UniqueConstraint(fields=("organization","reference"), name="deviation_reference_per_org")),
        migrations.AddConstraint(model_name="capa", constraint=models.UniqueConstraint(fields=("organization","reference"), name="capa_reference_per_org")),
        migrations.AddConstraint(model_name="changecontrol", constraint=models.UniqueConstraint(fields=("organization","reference"), name="change_reference_per_org")),
    ]
