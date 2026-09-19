from django.db import migrations, models
import django.db.models.deletion


def migrate_single_assignment(apps, schema_editor):
    Membership = apps.get_model("platform", "Membership")
    for membership in Membership.objects.all().iterator():
        sites = list(membership.sites.all())
        if len(sites) != 1:
            raise RuntimeError(
                f"Membership {membership.pk} cannot migrate: expected exactly one site, "
                f"found {len(sites)}."
            )
        site = sites[0]
        if site.organization_id != membership.organization_id:
            raise RuntimeError(
                f"Membership {membership.pk} cannot migrate: site {site.pk} "
                "belongs to another organization."
            )
        if membership.default_site_id and membership.default_site_id != site.pk:
            raise RuntimeError(
                f"Membership {membership.pk} cannot migrate: default site does not "
                "match the sole assigned site."
            )
        membership.site_id = site.pk
        membership.save(update_fields=["site"])


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_remove_customuser_role"),
        ("platform", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="role",
            name="scope",
            field=models.CharField(
                choices=[("SITE", "Site"), ("ORGANIZATION", "Organization")],
                default="SITE",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="membership",
            name="site",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="single_memberships",
                to="platform.site",
            ),
        ),
        migrations.RunPython(migrate_single_assignment, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="membership",
            name="sites",
        ),
        migrations.RemoveField(
            model_name="membership",
            name="default_site",
        ),
        migrations.AlterField(
            model_name="membership",
            name="site",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="memberships",
                to="platform.site",
            ),
        ),
        migrations.AlterField(
            model_name="membership",
            name="user",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="membership",
                to="accounts.customuser",
            ),
        ),
        migrations.RemoveConstraint(
            model_name="membership",
            name="one_membership_per_org",
        ),
        migrations.AddConstraint(
            model_name="membership",
            constraint=models.UniqueConstraint(
                fields=("user",),
                name="one_membership_per_user",
            ),
        ),
    ]
