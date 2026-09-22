from django.db import migrations, models
from django.db.models.functions import Lower


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0006_mfa"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="customuser",
            constraint=models.UniqueConstraint(Lower("email"), name="unique_user_email_lower"),
        ),
    ]
