from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("platform", "0001_initial"), ("batches", "0001_initial")]
    operations = [migrations.AddField(model_name="batch", name="organization", field=models.ForeignKey(blank=True, db_index=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="batches_batch_records", to="platform.organization"))]
