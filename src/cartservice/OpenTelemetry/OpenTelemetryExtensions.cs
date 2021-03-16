using System;
using cartservice.cartstore;
using Microsoft.Extensions.DependencyInjection;
using OpenTelemetry.Resources;
using OpenTelemetry.Trace;

namespace cartservice.OpenTelemetry
{
    public static class OpenTelemetryExtensions
    {
        private static (Uri endpoint, string headers) GetOptions()
        {
            var newRelicApiKey = Environment.GetEnvironmentVariable("NEW_RELIC_API_KEY");
            var otlpEndpoint = Environment.GetEnvironmentVariable("OTEL_EXPORTER_OTLP_ENDPOINT");
            return (new Uri(otlpEndpoint), $"api-key={newRelicApiKey}");
        }

        public static void AddOpenTelemetry(this IServiceCollection services, ICartStore cartStore)
        {
            services.AddOpenTelemetryTracing(builder => {
                builder.SetResourceBuilder(
                    ResourceBuilder
                        .CreateDefault()
                        .AddService("CartService"));
                
                builder.AddAspNetCoreInstrumentation();

                if (cartStore is RedisCartStore redisCartStore)
                {
                    builder.AddRedisInstrumentation(redisCartStore.ConnectionMultiplexer);
                }

                builder
                    .AddOtlpExporter(options => {
                        var opts = GetOptions();
                        options.Endpoint = opts.endpoint;
                        options.Headers = opts.headers;
                    });
            });
        }
    }
}
