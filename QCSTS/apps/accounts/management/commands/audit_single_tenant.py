from collections import defaultdict

from django.core.management.base import BaseCommand

from apps.accounts.models import CustomUser
from apps.platform.models import Membership


class Command(BaseCommand):
    help = (
        "Audit legacy customer authorization data before the single-"
        "organization/single-site/single-role migration."
    )

    def handle(self, *args, **options):
        failures = []

        for user in CustomUser.objects.order_by("email"):
            memberships = list(
                Membership.objects.filter(user=user)
                .select_related("organization", "role")
                .prefetch_related("sites")
            )

            if len(memberships) == 0:
                failures.append(
                    f"user {user.id} ({user.email}) has 0 memberships"
                )
                continue

            if len(memberships) > 1:
                failures.append(
                    f"user {user.id} ({user.email}) has {len(memberships)} memberships"
                )

            for membership in memberships:
                sites = list(membership.sites.all())
                default_site_id = membership.default_site_id

                if len(sites) == 0:
                    failures.append(
                        f"membership {membership.id} for {user.email} has no site"
                    )

                if len(sites) > 1:
                    failures.append(
                        f"membership {membership.id} for {user.email} has "
                        f"{len(sites)} sites"
                    )

                if default_site_id and default_site_id not in {site.id for site in sites}:
                    failures.append(
                        f"membership {membership.id} for {user.email} has a "
                        "default_site outside its sites relation"
                    )

                if (
                    membership.default_site_id
                    and membership.default_site.organization_id
                    != membership.organization_id
                ):
                    failures.append(
                        f"membership {membership.id} for {user.email} has a "
                        "default site belonging to another organization"
                    )

                if (
                    membership.role.organization_id
                    not in (None, membership.organization_id)
                ):
                    failures.append(
                        f"membership {membership.id} for {user.email} references "
                        "a role belonging to another organization"
                    )

        # Duplicate user/organization memberships are already forbidden by the
        # current constraint, but keep the check explicit so this command also
        # documents the migration invariant.
        duplicate_pairs = defaultdict(list)
        for membership in Membership.objects.all():
            duplicate_pairs[(membership.user_id, membership.organization_id)].append(
                membership.id
            )
        for (user_id, organization_id), ids in duplicate_pairs.items():
            if len(ids) > 1:
                failures.append(
                    f"user {user_id} has duplicate memberships for organization "
                    f"{organization_id}: {', '.join(map(str, ids))}"
                )

        if failures:
            self.stdout.write(self.style.ERROR("SINGLE-TENANT MIGRATION BLOCKED"))
            for failure in failures:
                self.stdout.write(f" - {failure}")
            self.stdout.write(
                self.style.ERROR(
                    f"\n{len(failures)} invariant violation(s) found. "
                    "Resolve them explicitly before applying the enforcing migration."
                )
            )
            raise SystemExit(1)

        self.stdout.write(
            self.style.SUCCESS(
                "Legacy authorization audit passed: every customer user has "
                "exactly one membership, exactly one site, and an organization-valid role."
            )
        )
