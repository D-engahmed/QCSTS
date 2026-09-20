from django.db import migrations, models


def validate_unique_active_locations(apps, schema_editor):
    Batch = apps.get_model("batches", "Batch")
    duplicates = (
        Batch.objects.filter(is_active=True)
        .values("organization_id", "shelf", "rack", "position")
        .annotate(total=models.Count("id"))
        .filter(total__gt=1)
    )
    if duplicates.exists():
        sample = list(duplicates.values_list("organization_id", "shelf", "rack", "position", "total")[:10])
        raise RuntimeError(
            "Cannot enforce unique active chamber locations. "
            f"Resolve duplicate locations first: {sample}"
        )


class Migration(migrations.Migration):
    dependencies = [("batches", "0003_alter_batch_organization")]

    operations = [
        migrations.RunPython(validate_unique_active_locations, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name="batch",
            constraint=models.UniqueConstraint(
                fields=("organization", "shelf", "rack", "position"),
                condition=models.Q(is_active=True),
                name="active_chamber_location_per_org",
            ),
        ),
    ]
