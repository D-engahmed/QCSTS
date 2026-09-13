from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("platform", "0001_initial"), ("chamber", "0001_initial")]
    operations = [
        migrations.AddField(model_name="samplepull", name="organization", field=models.ForeignKey(blank=True, db_index=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="chamber_samplepull_records", to="platform.organization")),
        migrations.AddField(model_name="locationhistory", name="organization", field=models.ForeignKey(blank=True, db_index=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="chamber_locationhistory_records", to="platform.organization")),
    ]
