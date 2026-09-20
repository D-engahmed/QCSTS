from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("batches", "0003_alter_batch_organization")]

    operations = [
        migrations.AddConstraint(
            model_name="batch",
            constraint=models.UniqueConstraint(
                fields=("organization", "shelf", "rack", "position"),
                condition=models.Q(is_active=True),
                name="active_chamber_location_per_org",
            ),
        ),
    ]
