from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace import TracerProvider

resource = Resource.create({"service.name": "reco-api", "service.version": "1.0.0", "deployment.environment": "prod"})

trace.set_tracer_provider(TracerProvider(resource=resource))
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint="http://otel-collector:4318/v1/traces"))
)

# Метрики
reader = PeriodicExportingMetricReader(OTLPMetricExporter(endpoint="http://otel-collector:4318/v1/metrics"))
metrics.set_meter_provider(MeterProvider(resource=resource, metric_readers=[reader]))