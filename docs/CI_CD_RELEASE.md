# QCSTS CI/CD and production release

## CI gates

Every pull request and every push to `main` runs:

1. Python 3.12 dependency installation with pip cache.
2. `pip check`.
3. Django `check --deploy`.
4. Migration drift detection with `makemigrations --check --dry-run`.
5. PostgreSQL migration execution.
6. Ruff linting.
7. Backend pytest with a 90% coverage floor.
8. Frontend `npm ci`.
9. TypeScript typecheck.
10. Next.js production build.
11. Backend and frontend Docker image builds.

The test suite uses PostgreSQL in CI rather than SQLite so database constraints and PostgreSQL migrations are exercised by the gate.

## Image publishing

A successful push to `main` publishes:

- `ghcr.io/<owner>/qcsts-backend:<commit-sha>`
- `ghcr.io/<owner>/qcsts-frontend:<commit-sha>`

Images are immutable by commit SHA. A deployment should pin both image variables to the same release SHA.

## Production stack

Use:

```text
QCSTS/docker/docker-compose.prod.yml
QCSTS/docker/nginx.prod.conf
QCSTS/.env.production
```

The production compose stack contains:

- PostgreSQL
- Redis with password authentication
- one-shot migration + collectstatic gate
- Django/Gunicorn
- Celery worker
- Celery Beat
- Next.js standalone frontend
- Nginx reverse proxy

The migration service must complete successfully before web, Celery or Celery Beat starts.

## Deployment command

After pulling the desired release:

```powershell
cd QCSTS/docker

$env:QCSTS_BACKEND_IMAGE="ghcr.io/<owner>/qcsts-backend:<release-sha>"
$env:QCSTS_FRONTEND_IMAGE="ghcr.io/<owner>/qcsts-frontend:<release-sha>"

docker compose --env-file ../.env.production -f docker-compose.prod.yml pull
docker compose --env-file ../.env.production -f docker-compose.prod.yml up -d
```

For a real internet deployment, terminate TLS at the load balancer/reverse proxy and forward `X-Forwarded-Proto: https`. The Django production settings intentionally redirect HTTP to HTTPS.

## Release invariants

Do not deploy a release when:

- CI is red.
- migration drift exists;
- the backend coverage gate is below 90%;
- the frontend production build fails;
- either container image fails to build;
- the production migration service fails.

The pipeline is a gate, not a substitute for application-level UAT and validation evidence.
