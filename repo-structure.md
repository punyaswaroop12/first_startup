# Repo Structure

```text
first_startup/
  apps/
    api/
      app/
        api/
        automation/
        core/
        db/
        ingestion/
        models/
        prompts/
        providers/
        schemas/
        services/
        utils/
      tests/
    web/
      src/
        app/
        components/
        lib/
      public/
  docs/
  infra/
    postgres/
  seed-data/
  storage/
    uploads/
    emails/
  .env.example
  docker-compose.yml
  project-plan.md
  architecture.md
  repo-structure.md
  CHECKLIST.md
  demo-script.md
  roadmap.md
```

## Responsibilities

- `apps/api`: business logic, persistence, ingestion, AI orchestration, automation engine
- `apps/web`: product UI and authenticated workflows
- `docs`: supplementary implementation notes if needed
- `infra/postgres`: local DB initialization
- `seed-data`: demo users, sample docs, and seed fixtures
- `storage`: local development artifact storage
