from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("billing", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="invoice",
            name="provider_order_id",
            field=models.CharField(blank=True, max_length=255, unique=True, null=True),
        ),
        migrations.AddField(
            model_name="invoice",
            name="provider_transaction_id",
            field=models.CharField(blank=True, max_length=255, unique=True, null=True),
        ),
    ]
