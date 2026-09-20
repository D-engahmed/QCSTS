from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("accounts", "0003_customuser_locked_until")]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="password_changed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
