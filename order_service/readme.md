### Sentry

Error tracking is configured via [Sentry](https://sentry.io). When a `SENTRY_DSN` is present the SDK initialises automatically on startup and captures all unhandled exceptions with full request context (method, URL, headers, stack trace). When `SENTRY_DSN` is absent the service starts normally with no Sentry overhead — so it is safe to omit in local development.

#### Setup

1. Create a project at [sentry.io](https://sentry.io) (or use a self-hosted instance) and copy the DSN from **Settings → Projects → \<your project\> → Client Keys**.

2. Add the DSN to `order_service/.env`:
```
SENTRY_DSN=https://<key>@<org>.ingest.sentry.io/<project-id>
```

3. Start the service. Docker Compose passes the `.env` file through via `env_file`, so no changes to `docker-compose.yml` are needed:
```bash
docker-compose up order-service
```

The SDK is initialised before the first request is served. Sentry is used for error tracking only; traces come from OpenTelemetry (see the main readme). Any unhandled exception — including failures in the outbox worker while publishing to RabbitMQ — will appear in your Sentry dashboard within seconds.

#### Disabling Sentry

Remove or comment out `SENTRY_DSN` in `.env`. The service will start without initialising the SDK.

### Outbox Pattern

When an order is created, the order and its RabbitMQ event are saved together in the database. The `outbox-worker` then reads pending events and publishes them to RabbitMQ. Events remain pending and are retried if publishing fails, so a successfully saved order is not lost when RabbitMQ is temporarily unavailable.

---

### Useful Timescale DB Shell Commands

1. Enter TimescaleDB shell:
```bash
psql -U <db user>
```
E.g.
```bash
psql -U <postgres>
```

2. Connect to your desired database:
```bash
\c <db name>
```
E.g.
```bash
\c orders
```

3. List tables:
```bash
\dt
```

### Useful RabbitMQ Shell Commands

1. List Exchanges:
```bash
rabbitmqctl list_exchanges
```
