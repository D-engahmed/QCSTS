from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_customuser_locked_until"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="customuser",
            name="role",
        ),
    ]
