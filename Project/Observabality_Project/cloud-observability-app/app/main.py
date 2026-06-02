import json
import logging
import os
import random
import time

from fastapi import FastAPI, HTTPException
from prometheus_client import Counter, Histogram, generate_latest
from starlette.responses import Response

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter


# ─────────────────────────────────────────────
# TRACING SETUP (OpenTelemetry → OTel Collector → Jaeger → Elastic)
# ─────────────────────────────────────────────

# Give this service a name — shows up in Jaeger UI
resource = Resource.create({"service.name": "observability-demo-app"})

trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

# Endpoint is read from env var — so Helm chart can override it without code change
otlp_exporter = OTLPSpanExporter(
    endpoint="http://otel-collector-opentelemetry-collector.traces.svc.cluster.local:4318/v1/traces"
)

trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(otlp_exporter))

# ─────────────────────────────────────────────
# APP SETUP
# ─────────────────────────────────────────────

app = FastAPI()

# Auto-instruments every route — creates spans automatically for all requests
FastAPIInstrumentor.instrument_app(app)

# Injects trace_id + span_id into every log line automatically
# This is what connects your logs (Kibana) ↔ traces (Jaeger)
LoggingInstrumentor().instrument(set_logging_format=True)

# ─────────────────────────────────────────────
# LOGGING SETUP — JSON format for EFK
# ─────────────────────────────────────────────
# Plain text logs are hard to filter in Kibana
# JSON lets you query: trace_id="abc123" AND level="ERROR"

class JSONFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "trace_id": getattr(record, "otelTraceID", ""),   # injected by LoggingInstrumentor
            "span_id": getattr(record, "otelSpanID", ""),     # injected by LoggingInstrumentor
            "service": "observability-demo-app"
        })

handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())

logger = logging.getLogger("demo-app")
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# ─────────────────────────────────────────────
# METRICS SETUP (Prometheus)
# ─────────────────────────────────────────────
# Labels (endpoint, method) let Grafana filter per route
# Without labels, you only see total counts — not useful

REQUEST_COUNT = Counter(
    "app_requests_total",
    "Total requests per endpoint",
    ["endpoint", "method"]   # label = filter key in Grafana
)

ERROR_COUNT = Counter(
    "app_errors_total",
    "Total errors per endpoint",
    ["endpoint"]
)

REQUEST_LATENCY = Histogram(
    "app_request_latency_seconds",
    "Request latency per endpoint",
    ["endpoint"]
)

# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────

@app.get("/")
def home():
    return {"message": "Observability Demo Running"}


@app.get("/health")
def health():
    # Kubernetes liveness/readiness probe hits this
    return {"status": "UP"}


@app.get("/metrics")
def metrics():
    # Prometheus scrapes this endpoint to collect all metrics
    return Response(generate_latest(), media_type="text/plain")


@app.get("/api/orders")
def orders():
    endpoint = "/api/orders"

    REQUEST_COUNT.labels(endpoint=endpoint, method="GET").inc()

    with REQUEST_LATENCY.labels(endpoint=endpoint).time():
        # Span = one unit of work in a trace
        # This span will appear as a child under the auto-instrumented HTTP span in Jaeger
        with tracer.start_as_current_span("orders-processing") as span:
            processing_time = random.uniform(0.2, 1.5)
            time.sleep(processing_time)

            # Attributes appear as tags inside the span in Jaeger UI
            span.set_attribute("order.processing_time_seconds", round(processing_time, 2))
            span.set_attribute("order.simulated", True)

            # trace_id + span_id auto-added by LoggingInstrumentor
            # So this log line is searchable in Kibana by trace_id
            logger.info(f"Order processed in {processing_time:.2f}s")

            return {"status": "success", "processing_time": processing_time}


@app.get("/api/orders/{order_id}")
def get_order(order_id: str):
    endpoint = "/api/orders/:id"

    REQUEST_COUNT.labels(endpoint=endpoint, method="GET").inc()

    with tracer.start_as_current_span("get-order") as span:
        span.set_attribute("order.id", order_id)

        # 30% random failure — lets you demo error spike in Grafana + failed trace in Jaeger
        if random.random() < 0.3:
            span.set_status(trace.StatusCode.ERROR, "Order not found")  # marks span red in Jaeger
            ERROR_COUNT.labels(endpoint=endpoint).inc()
            logger.error(f"Order {order_id} not found")                 # appears in Kibana as ERROR
            raise HTTPException(status_code=404, detail="Order not found")

        logger.info(f"Fetched order {order_id}")
        return {"order_id": order_id, "status": "delivered"}