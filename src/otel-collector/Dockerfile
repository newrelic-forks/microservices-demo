FROM otel/opentelemetry-collector-contrib:0.26.0

ARG NEW_RELIC_API_KEY
ARG NEW_RELIC_TRACE_HOST
ARG NEW_RELIC_METRIC_HOST
ARG OTEL_EXPORTER_OTLP_SPAN_ENDPOINT_NO_SCHEME

ENV NEW_RELIC_API_KEY=${NEW_RELIC_API_KEY}
ENV NEW_RELIC_TRACE_HOST=${NEW_RELIC_TRACE_HOST}
ENV NEW_RELIC_METRIC_HOST=${NEW_RELIC_METRIC_HOST}
ENV OTEL_EXPORTER_OTLP_SPAN_ENDPOINT_NO_SCHEME=${OTEL_EXPORTER_OTLP_SPAN_ENDPOINT_NO_SCHEME}

COPY ./collector.yaml /etc/otel/config.yaml

ENTRYPOINT ["/otelcontribcol"]
CMD ["--config", "/etc/otel/config.yaml"]
EXPOSE 55680 55679 9411 14250 14268 13133 4317
