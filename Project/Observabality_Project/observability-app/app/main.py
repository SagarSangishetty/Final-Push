import logging
import random
import time

from fastapi import FastAPI
from prometheus_client import Counter, Histogram, generate_latest
from starlette.responses import Response

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor

resource = Resource.create({
    "service.name": "observability-demo-app"
})

trace.set_tracer_provider(
    TracerProvider(resource=resource)
)

tracer = trace.get_tracer(__name__)

otlp_exporter = OTLPSpanExporter(
    endpoint="otel-collector-opentelemetry-collector.traces.svc.cluster.local:4317",
    insecure=True
)

span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

app = FastAPI()

FastAPIInstrumentor.instrument_app(app)
LoggingInstrumentor().instrument(set_logging_format=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("demo-app")

REQUEST_COUNT = Counter(
    "app_requests_total",
    "Total application requests"
)

REQUEST_LATENCY = Histogram(
    "app_request_latency_seconds",
    "Application request latency"
)

@app.get("/")
def home():
    return {"message": "Observability Demo Running"}

@app.get("/health")
def health():
    return {"status": "UP"}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")

@app.get("/api/orders")
@REQUEST_LATENCY.time()
def orders():
    REQUEST_COUNT.inc()

    with tracer.start_as_current_span("orders-processing"):
        processing_time = random.uniform(0.2, 1.5)

        time.sleep(processing_time)

        logger.info(
            f"Order processed successfully in {processing_time:.2f}s"
        )

        return {
            "status": "success",
            "processing_time": processing_time
        }
