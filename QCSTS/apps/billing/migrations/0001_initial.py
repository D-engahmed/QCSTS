import uuid
from decimal import Decimal

import django.db.models.deletion
from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("platform", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Plan",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("code", models.CharField(choices=[("essential", "Essential"), ("professional", "Professional"), ("enterprise", "Enterprise")], max_length=32, unique=True)),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True)),
                ("monthly_price", models.DecimalField(decimal_places=2, max_digits=12)),
                ("annual_price", models.DecimalField(decimal_places=2, max_digits=12)),
                ("currency", models.CharField(default="USD", max_length=3)),
                ("max_users", models.PositiveIntegerField(blank=True, null=True)),
                ("max_sites", models.PositiveIntegerField(blank=True, null=True)),
                ("max_studies", models.PositiveIntegerField(blank=True, null=True)),
                ("max_storage_mb", models.PositiveIntegerField(blank=True, null=True)),
                ("api_access", models.BooleanField(default=False)),
                ("active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"db_table": "billing_plan", "ordering": ["monthly_price"]},
        ),
        migrations.CreateModel(
            name="Subscription",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("status", models.CharField(choices=[("trialing", "Trialing"), ("active", "Active"), ("past_due", "Past due"), ("suspended", "Suspended"), ("canceled", "Canceled"), ("expired", "Expired")], default="trialing", max_length=16)),
                ("interval", models.CharField(choices=[("month", "Monthly"), ("year", "Yearly")], default="year", max_length=8)),
                ("provider", models.CharField(default="manual", max_length=32)),
                ("provider_subscription_id", models.CharField(blank=True, max_length=255)),
                ("trial_ends_at", models.DateTimeField(blank=True, null=True)),
                ("current_period_start", models.DateTimeField(blank=True, null=True)),
                ("current_period_end", models.DateTimeField(blank=True, null=True)),
                ("cancel_at_period_end", models.BooleanField(default=False)),
                ("canceled_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("organization", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="subscriptions", to="platform.organization")),
                ("plan", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="subscriptions", to="billing.plan")),
            ],
            options={"db_table": "billing_subscription"},
        ),
        migrations.CreateModel(
            name="Invoice",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("number", models.CharField(max_length=64, unique=True)),
                ("status", models.CharField(choices=[("draft", "Draft"), ("open", "Open"), ("paid", "Paid"), ("void", "Void"), ("uncollectible", "Uncollectible")], default="draft", max_length=20)),
                ("currency", models.CharField(default="USD", max_length=3)),
                ("subtotal", models.DecimalField(decimal_places=2, max_digits=12)),
                ("tax", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=12)),
                ("total", models.DecimalField(decimal_places=2, max_digits=12)),
                ("due_at", models.DateTimeField(blank=True, null=True)),
                ("paid_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("organization", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="invoices", to="platform.organization")),
                ("subscription", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="invoices", to="billing.subscription")),
            ],
            options={"db_table": "billing_invoice"},
        ),
        migrations.CreateModel(
            name="PaymentEvent",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("provider", models.CharField(max_length=32)),
                ("event_id", models.CharField(max_length=255)),
                ("event_type", models.CharField(max_length=120)),
                ("payload", models.JSONField(default=dict)),
                ("processed", models.BooleanField(default=False)),
                ("processed_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("organization", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="payment_events", to="platform.organization")),
            ],
            options={"db_table": "billing_payment_event"},
        ),
        migrations.CreateModel(
            name="UsageRecord",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("metric", models.CharField(max_length=64)),
                ("period_start", models.DateTimeField()),
                ("period_end", models.DateTimeField()),
                ("quantity", models.PositiveBigIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("organization", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="usage_records", to="platform.organization")),
            ],
            options={"db_table": "billing_usage_record"},
        ),
        migrations.AddConstraint(
            model_name="subscription",
            constraint=models.UniqueConstraint(
                condition=Q(status__in=["trialing", "active", "past_due"]),
                fields=("organization",),
                name="one_current_subscription_per_org",
            ),
        ),
        migrations.AddConstraint(
            model_name="paymentevent",
            constraint=models.UniqueConstraint(fields=("provider", "event_id"), name="unique_billing_provider_event"),
        ),
        migrations.AddConstraint(
            model_name="usagerecord",
            constraint=models.UniqueConstraint(fields=("organization", "metric", "period_start", "period_end"), name="unique_usage_window"),
        ),
        migrations.AddIndex(model_name="subscription", index=models.Index(fields=["organization", "status"], name="billing_sub_organiz_1e4e9e_idx")),
        migrations.AddIndex(model_name="subscription", index=models.Index(fields=["current_period_end"], name="billing_sub_curren_6bc76d_idx")),
        migrations.AddIndex(model_name="invoice", index=models.Index(fields=["organization", "status"], name="billing_inv_organiz_2e57d1_idx")),
        migrations.AddIndex(model_name="paymentevent", index=models.Index(fields=["organization", "processed"], name="billing_pay_organiz_67f6aa_idx")),
        migrations.AddIndex(model_name="usagerecord", index=models.Index(fields=["organization", "metric", "period_end"], name="billing_use_organiz_3c3dd1_idx")),
    ]
