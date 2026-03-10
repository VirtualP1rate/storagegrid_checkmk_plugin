#!/usr/bin/env python3
"""
CheckMK Graph Templates for StorageGRID Tenant Usage
"""

from cmk.graphing.v1 import graphs, metrics, Title
from cmk.graphing.v1.metrics import (
    Color,
    DecimalNotation,
    IECNotation,
    Metric,
    StrictPrecision,
    Unit,
)
from cmk.graphing.v1.graphs import Graph, MinimalRange

metric_data_bytes = Metric(
    name="data_bytes",
    title=Title("Used Storage"),
    unit=Unit(IECNotation("B")),
    color=Color.BLUE,
)

metric_quota_utilization = Metric(
    name="quota_utilization",
    title=Title("Quota Utilization"),
    unit=Unit(DecimalNotation("%"), StrictPrecision(2)),
    color=Color.GREEN,
)

metric_object_count = Metric(
    name="object_count",
    title=Title("Object Count"),
    unit=Unit(DecimalNotation("")),
    color=Color.ORANGE,
)

graph_tenant_quota = Graph(
    name="storagegrid_tenant_quota",
    title=Title("Tenant Quota Utilization"),
    compound_lines=["quota_utilization"],
    minimal_range=MinimalRange(0, 100),
)

graph_tenant_storage = Graph(
    name="storagegrid_tenant_storage",
    title=Title("Tenant Storage Usage"),
    compound_lines=["data_bytes"],
)

graph_tenant_objects = Graph(
    name="storagegrid_tenant_objects",
    title=Title("Tenant Object Count"),
    compound_lines=["object_count"],
)
