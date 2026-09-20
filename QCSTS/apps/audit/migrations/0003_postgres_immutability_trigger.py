from django.db import migrations


SQL = r"""
CREATE OR REPLACE FUNCTION qcsts_prevent_audit_mutation()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION 'QCSTS audit log records are immutable';
END;
$$;

DROP TRIGGER IF EXISTS audit_log_immutable ON audit_log;

CREATE TRIGGER audit_log_immutable
BEFORE UPDATE OR DELETE ON audit_log
FOR EACH ROW
EXECUTE FUNCTION qcsts_prevent_audit_mutation();
"""

REVERSE_SQL = r"""
DROP TRIGGER IF EXISTS audit_log_immutable ON audit_log;
DROP FUNCTION IF EXISTS qcsts_prevent_audit_mutation();
"""


class Migration(migrations.Migration):
    dependencies = [
        ("audit", "0002_add_organization_boundary"),
    ]

    operations = [
        migrations.RunSQL(SQL, REVERSE_SQL),
    ]
