package hipstershop;

import io.opentelemetry.api.OpenTelemetry;
import io.opentelemetry.api.common.AttributeKey;
import io.opentelemetry.api.common.Attributes;
import io.opentelemetry.api.metrics.Meter;
import io.opentelemetry.api.metrics.ObservableLongMeasurement;
import java.lang.management.ManagementFactory;
import java.lang.management.MemoryPoolMXBean;
import java.lang.management.MemoryType;
import java.lang.management.MemoryUsage;
import java.util.ArrayList;
import java.util.List;
import java.util.function.Consumer;
import java.util.function.Function;

public final class MemoryPools {

  private static final AttributeKey<String> TYPE_KEY = AttributeKey.stringKey("type");
  private static final AttributeKey<String> POOL_KEY = AttributeKey.stringKey("pool");

  private static final String HEAP = "heap";
  private static final String NON_HEAP = "non_heap";

  /** Register observers for java runtime memory metrics. */
  public static void registerObservers(OpenTelemetry openTelemetry) {
    registerObservers(openTelemetry, ManagementFactory.getMemoryPoolMXBeans());
  }

  // Visible for testing
  static void registerObservers(OpenTelemetry openTelemetry, List<MemoryPoolMXBean> poolBeans) {
    Meter meter = openTelemetry.getMeter("io.opentelemetry.runtime-metrics");

    meter
        .upDownCounterBuilder("process.runtime.jvm.memory.usage_after_gc")
        .setDescription(
            "Measure of memory used after the most recent garbage collection event on the pool")
        .setUnit("By")
        .buildWithCallback(callback(poolBeans, MemoryUsage::getUsed));
  }

  // Visible for testing
  static Consumer<ObservableLongMeasurement> callback(
      List<MemoryPoolMXBean> poolBeans, Function<MemoryUsage, Long> extractor) {
    List<Attributes> attributeSets = new ArrayList<>(poolBeans.size());
    for (MemoryPoolMXBean pool : poolBeans) {
      attributeSets.add(
          Attributes.builder()
              .put(POOL_KEY, pool.getName())
              .put(TYPE_KEY, memoryType(pool.getType()))
              .build());
    }

    return measurement -> {
      for (int i = 0; i < poolBeans.size(); i++) {
        Attributes attributes = attributeSets.get(i);
        MemoryUsage memoryUsage = poolBeans.get(i).getCollectionUsage();
        if (memoryUsage == null) {
          continue;
        }
        long value = extractor.apply(memoryUsage);
        if (value != -1) {
          measurement.record(value, attributes);
        }
      }
    };
  }

  private static String memoryType(MemoryType memoryType) {
    switch (memoryType) {
      case HEAP:
        return HEAP;
      case NON_HEAP:
        return NON_HEAP;
    }
    return "unknown";
  }

  private MemoryPools() {}
}
