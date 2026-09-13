from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("platform", "0001_initial"), ("schedule", "0002_alter_testpoint_status")]
    operations = [migrations.AddField(model_name="testpoint", name="organization", field=models.ForeignKey(blank=True, db_index=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="schedule_testpoint_records", to="platform.organization"))]
