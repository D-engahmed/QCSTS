from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("platform", "0001_initial"), ("results", "0001_initial")]
    operations = [migrations.AddField(model_name="testresult", name="organization", field=models.ForeignKey(blank=True, db_index=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="results_testresult_records", to="platform.organization"))]
