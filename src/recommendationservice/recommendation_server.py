#!/usr/bin/python
#
# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import random
import time
import traceback
from concurrent import futures
from urllib.parse import urlparse

import demo_pb2
import demo_pb2_grpc
import grpc
from exporter import NewRelicSpanExporter
from logger import getJSONLogger
from opentelemetry import trace
from opentelemetry.instrumentation.grpc import GrpcInstrumentorServer
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchExportSpanProcessor

logger = getJSONLogger("recommendationservice-server")


trace.set_tracer_provider(
    TracerProvider(resource=Resource.create({"service.name": "recommendationservice"}))
)
trace.get_tracer_provider().add_span_processor(
    BatchExportSpanProcessor(
        NewRelicSpanExporter(
            os.environ["NEW_RELIC_API_KEY"],
            host=urlparse(os.environ["NEW_RELIC_TRACE_URL"]).hostname,
        ),
        schedule_delay_millis=500,
    )
)
grpc_server_instrumentor = GrpcInstrumentorServer()
grpc_server_instrumentor.instrument()


class RecommendationService(demo_pb2_grpc.RecommendationServiceServicer):
    def ListRecommendations(self, request, context):
        max_responses = 5
        # fetch list of products from product catalog stub
        cat_response = product_catalog_stub.ListProducts(demo_pb2.Empty())
        product_ids = [x.id for x in cat_response.products]
        filtered_products = list(set(product_ids) - set(request.product_ids))
        num_products = len(filtered_products)
        num_return = min(max_responses, num_products)
        # sample list of indicies to return
        indices = random.sample(range(num_products), num_return)
        # fetch product ids from indices
        prod_list = [filtered_products[i] for i in indices]
        logger.info("[Recv ListRecommendations] product_ids={}".format(prod_list))
        # build and return response
        response = demo_pb2.ListRecommendationsResponse()
        response.product_ids.extend(prod_list)
        return response


if __name__ == "__main__":
    logger.info("initializing recommendationservice")

    port = os.environ.get("PORT", "8080")
    catalog_addr = os.environ.get("PRODUCT_CATALOG_SERVICE_ADDR", "")
    if catalog_addr == "":
        raise Exception("PRODUCT_CATALOG_SERVICE_ADDR environment variable not set")
    logger.info("product catalog address: " + catalog_addr)
    channel = grpc.insecure_channel(catalog_addr)
    product_catalog_stub = demo_pb2_grpc.ProductCatalogServiceStub(channel)

    # create gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # add class to gRPC server
    service = RecommendationService()
    demo_pb2_grpc.add_RecommendationServiceServicer_to_server(service, server)

    # start server
    logger.info("listening on port: " + port)
    server.add_insecure_port("[::]:" + port)
    server.start()

    # keep alive
    try:
        while True:
            time.sleep(10000)
    except KeyboardInterrupt:
        server.stop(0)
