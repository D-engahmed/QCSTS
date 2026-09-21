from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0004_customuser_password_changed_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="email_verified_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name="EmailVerificationToken",
            fields=[
                ("id", models.UUIDField(default=__import__("uuid").uuid4, editable=False, primary_key=True, serialize=False)),
                ("token_hash", models.CharField(max_length=64, unique=True)),
                ("expires_at", models.DateTimeField()),
                ("used_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="email_verification_tokens", to="accounts.customuser")),
            ],
            options={
                "db_table": "accounts_email_verification_token",
            },
        ),
        migrations.AddIndex(
            model_name="emailverificationtoken",
            index=models.Index(fields=["user", "expires_at"], name="accounts_em_user_id_6c50a7_idx"),
        ),
    ]
