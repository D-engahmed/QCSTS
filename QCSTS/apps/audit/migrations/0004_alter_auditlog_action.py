from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("audit", "0003_postgres_immutability_trigger"),
    ]

    operations = [
        migrations.AlterField(
            model_name="auditlog",
            name="action",
            field=models.CharField(
                choices=[
                    ("CREATE", "Create"),
                    ("UPDATE", "Update"),
                    ("DELETE", "Delete"),
                    ("LOGIN", "Login"),
                    ("LOGOUT", "Logout"),
                    ("SIGN", "Electronic Signature"),
                    ("APPROVE", "Approve"),
                    ("REJECT", "Reject"),
                    ("PASSWORD_CHANGED", "Password Changed"),
                    ("PASSWORD_RESET", "Password Reset"),
                    ("EMAIL_VERIFIED", "Email Verified"),
                    ("MFA_SETUP_STARTED", "MFA Setup Started"),
                    ("MFA_ENABLED", "MFA Enabled"),
                    ("MFA_DISABLED", "MFA Disabled"),
                ],
                max_length=20,
            ),
        ),
    ]
}
