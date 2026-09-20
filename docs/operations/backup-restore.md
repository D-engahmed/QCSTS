# QCSTS Backup / Restore Runbook

## Backup

Run from the repository root:

    bash QCSTS/docker/backup_postgres.sh

The script creates a PostgreSQL custom-format dump under QCSTS/backups with a UTC timestamp. Backups must be copied to storage outside the application host. A Docker volume alone is not a disaster-recovery strategy.

## Restore verification

Restore into an isolated PostgreSQL environment before restoring production traffic:

    bash QCSTS/docker/restore_postgres.sh QCSTS/backups/<backup>.dump

Then run Django checks and migration checks, followed by application smoke tests. Verify organizations, subscriptions, studies, results, audit records, and recent payment events.

## RPO/RTO

Do not invent RPO/RTO numbers. Measure them. Record the maximum acceptable data loss from the backup schedule and the elapsed recovery time from declaring recovery to passing application smoke tests.

A backup is not considered verified until it has been restored successfully in an isolated environment.

## Operational requirement

Schedule backups outside the application container lifecycle, retain multiple generations, and store at least one copy outside the production host or account boundary.
