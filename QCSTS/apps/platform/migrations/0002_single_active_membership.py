from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("platform", "0001_initial")]

    operations = [
        migrations.AddConstraint(
            model_name="membership",
            constraint=models.UniqueConstraint(
                fields=("user",),
                condition=models.Q(is_active=True),
                name="one_active_membership_per_user",
            ),
        ),
    ]
