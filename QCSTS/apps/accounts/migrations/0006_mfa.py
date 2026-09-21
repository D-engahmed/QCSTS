from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0005_email_verification"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="mfa_enabled",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="customuser",
            name="mfa_secret_encrypted",
            field=models.TextField(blank=True),
        ),
    ]
