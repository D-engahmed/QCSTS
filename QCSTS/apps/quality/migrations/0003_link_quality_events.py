from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("quality", "0002_alter_capa_options_alter_changecontrol_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="deviation",
            name="source_oos",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.PROTECT,
                related_name="deviations",
                to="quality.oosinvestigation",
            ),
        ),
        migrations.AddField(
            model_name="capa",
            name="source_deviation",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.PROTECT,
                related_name="capas",
                to="quality.deviation",
            ),
        ),
    ]
