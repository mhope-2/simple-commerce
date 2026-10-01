# Simple Commerce
Simple commerce simulates placing an order, saving the order to the database and then publishing it to a RabbitMQ.

### API Docs
[x] User Service: `http://localhost:8081/docs`  
[x] Product Service: `http://localhost:8082/docs`  
[x] Order Service: `http://localhost:8083/docs` 

### Order Service POST Request Sample
```json
{
  "user_id": "7c11e1ce2741",
  "product_code": "product1",
  "quantity": 2
}
```

## How to set up

### With Docker
1. Clone the repository
```bash
git clone https://github.com/mhope-2/simple-commerce.git
```
2. Build services
```bash
docker-compose build
```
3. Startup services using docker
```bash
docker-compose up
```

## Observability

All three services use FastAPI's native [OpenTelemetry support](https://fastapi.tiangolo.com/advanced/opentelemetry/) and send traces, metrics and logs over OTLP to an OpenTelemetry Collector, which forwards them:

| Signal | Path | Where to look |
|---|---|---|
| Traces | Collector → Tempo | Grafana → Explore → Tempo (`http://localhost:3000`, admin/admin) |
| Metrics | Collector → Prometheus | Grafana → Explore → Prometheus, or `http://localhost:9090` |
| Logs | Collector → Loki | Grafana → Explore → Loki |

- **One trace per order:** `POST /orders/` in the order service, its calls to the user and product services (which continue the trace), the database queries and the RabbitMQ publish all appear in the same trace. The order service instruments httpx, SQLAlchemy and pika for this (`order_service/app/config/telemetry.py`); the trace context also travels in the RabbitMQ message headers.
- **Metrics:** `http_server_request_duration_seconds` (histogram) and `http_server_active_requests` per service, labelled with `service_name`, `http_route`, `http_request_method` and `http_response_status_code`.
- **Logs:** the order service's JSON logs on stdout include `trace_id` and `span_id`, and are also sent to Loki. In Grafana, a log line links to its trace and a span links to its logs.
- **Configuration:** the standard `OTEL_*` environment variables, set in `docker-compose.yml` (`OTEL_SERVICE_NAME`, `OTEL_EXPORTER_OTLP_ENDPOINT`, ...). Without `OTEL_EXPORTER_OTLP_ENDPOINT` the services run without exporting anything. Sentry, when `SENTRY_DSN` is set, is used for error tracking only.

### Dashboard, business metrics and alerts

- **Grafana dashboard:** "Simple Commerce" (folder of the same name), provisioned from `monitoring/grafana/dashboards/`. It has a service filter and shows:
  - request rate, 5xx error ratio, p50/p95/p99 latency and active requests, per service and per route
  - orders created and failed, RabbitMQ publishes by outcome, dependency retries, and the latency of the order service's calls to the user and product services
  - error logs from Loki, each linked to its trace
- **Business metrics (order service, `app/config/metrics.py`):**

  | Metric | Labels | Meaning |
  |---|---|---|
  | `orders_created_total` | `product_code` | Orders saved |
  | `orders_failed_total` | `error_type` | Order requests that failed: a dependency's HTTP status (`404`, `500`, ...), `database`, `missing_user_or_product`, or an exception class |
  | `orders_messages_published_total` | `outcome` | Order messages sent to RabbitMQ, `success` or `failure` after retries |
  | `orders_dependency_retries_total` | `dependency` | Retried calls to `user-service`, `product-service` or `rabbitmq` |

- **Alert rules** (`monitoring/prometheus/rules/alerts.yml`, see Prometheus → Alerts):

  | Alert | Condition |
  |---|---|
  | `HighErrorRate` | over 5% of a service's requests return 5xx for 5 minutes |
  | `HighLatency` | a service's p95 latency is over 1 second for 10 minutes |
  | `OrderMessagePublishFailures` | any order message failed to reach RabbitMQ in the last 5 minutes |
  | `HighOrderFailureRate` | over 10% of order requests fail for 10 minutes |
  | `CollectorDown` | Prometheus cannot scrape the OpenTelemetry Collector |

  No Alertmanager is configured, so alerts show in Prometheus but are not sent anywhere.
