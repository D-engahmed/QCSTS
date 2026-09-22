from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("notifications", "0002_alter_notification_created_at_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notification",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True,
                help_text="Timestamp when this record was created. Set by server, never editable.",
            ),
        ),
    ]
