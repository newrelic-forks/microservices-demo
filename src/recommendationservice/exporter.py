import time
import typing

from newrelic_telemetry_sdk import Span as NewRelicSpan
from newrelic_telemetry_sdk import SpanClient
from opentelemetry import trace as trace_api
from opentelemetry.sdk.trace.export import Span, SpanExporter, SpanExportResult
from opentelemetry.trace.status import StatusCanonicalCode


class NewRelicSpanExporter(SpanExporter):
    def __init__(self, *args, **kwargs):
        self.client = SpanClient(*args, **kwargs)

    @staticmethod
    def _transform(span):
        attributes = dict(span.resource.attributes)
        attributes.update(span.attributes)

        context = span.get_span_context()
        start_time = span.start_time
        duration = span.end_time - start_time
        start_time = start_time // 10 ** 6
        duration = duration // 10 ** 6
        if span.parent:
            parent_id = "{:016x}".format(span.parent.span_id)
        else:
            parent_id = None

        if span.status.canonical_code is not StatusCanonicalCode.OK:
            attributes.setdefault("error", True)
            exc_type, exc_val = span.status.description.split(": ", 1)
            attributes.setdefault("error.type", exc_type)
            attributes.setdefault("error.msg", exc_val)

        return NewRelicSpan(
            name=span.name,
            tags=attributes,
            guid="{:016x}".format(context.span_id),
            trace_id="{:032x}".format(context.trace_id),
            parent_id=parent_id,
            start_time_ms=start_time,
            duration_ms=duration,
        )

    def export(self, spans: typing.Sequence[Span]) -> SpanExportResult:
        spans = [self._transform(span) for span in spans]
        response = self.client.send_batch(spans)
        response.raise_for_status()
        return SpanExportResult.SUCCESS