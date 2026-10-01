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
