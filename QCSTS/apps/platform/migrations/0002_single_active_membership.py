from django.db import migrations, models


def validate_single_active_membership(apps, schema_editor):
    Membership = apps.get_model("platform", "Membership")
    duplicates = (
        Membership.objects.filter(is_active=True)
        .values("user_id")
        .annotate(total=models.Count("id"))
        .filter(total__gt=1)
    )
    if duplicates.exists():
        sample = list(duplicates.values_list("user_id", "total")[:10])
        raise RuntimeError(
            "Cannot enforce one active tenant membership per user. "
            f"Resolve duplicate active memberships first: {sample}"
        )


class Migration(migrations.Migration):
    dependencies = [("platform", "0001_initial")]

    operations = [
        migrations.RunPython(validate_single_active_membership, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name="membership",
            constraint=models.UniqueConstraint(
                fields=("user",),
                condition=models.Q(is_active=True),
                name="one_active_membership_per_user",
            ),
        ),
    ]
