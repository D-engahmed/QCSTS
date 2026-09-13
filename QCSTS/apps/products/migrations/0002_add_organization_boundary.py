from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("platform", "0001_initial"), ("products", "0001_initial")]
    operations = [
        migrations.AddField(model_name="monograph", name="organization", field=models.ForeignKey(blank=True, db_index=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="products_monograph_records", to="platform.organization")),
        migrations.AddField(model_name="monographtest", name="organization", field=models.ForeignKey(blank=True, db_index=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="products_monographtest_records", to="platform.organization")),
        migrations.AddField(model_name="product", name="organization", field=models.ForeignKey(blank=True, db_index=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="products_product_records", to="platform.organization")),
    ]
