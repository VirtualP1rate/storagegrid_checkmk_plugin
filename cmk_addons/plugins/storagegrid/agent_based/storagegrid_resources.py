#!/usr/bin/env python3
"""
CheckMK Check Plugin for StorageGRID Node Resources
CheckMK 2.4.0 API (agent_based v2)
"""

import json

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    Service,
    Result,
    State,
    Metric,
    CheckResult,
    DiscoveryResult,
    StringTable,
)


def parse_storagegrid_resources(string_table: StringTable) -> dict | None:
    """Parse node resource data"""
    if not string_table:
        return None

    try:
        return json.loads(string_table[0][0])
    except (IndexError, json.JSONDecodeError, ValueError):
        return None


def discover_storagegrid_node_resources(section: dict) -> DiscoveryResult:
    """Discover node resource services"""
    if not section or 'error' in section:
        return

    for node in section.get('nodes', []):
        node_name = node.get('node')
        if node_name:
            yield Service(item=node_name)


def check_storagegrid_node_resources(item: str, params: dict, section: dict) -> CheckResult:
    """Check node resource utilization"""
    if not section:
        yield Result(state=State.UNKNOWN, summary="No data available")
        return

    if 'error' in section:
        yield Result(state=State.UNKNOWN, summary=f"Error: {section['error']}")
        return

    for node in section.get('nodes', []):
        if node.get('node') != item:
            continue

        cpu_percent = node.get('cpu_percent')
        memory_bytes = node.get('memory_bytes')

        if cpu_percent is not None:
            # Get thresholds
            warn, crit = params.get('cpu_levels', (80.0, 90.0))

            # Determine state
            if cpu_percent >= crit:
                state = State.CRIT
            elif cpu_percent >= warn:
                state = State.WARN
            else:
                state = State.OK

            # Build summary
            summary = f"CPU: {cpu_percent:.1f}%"
            if state != State.OK:
                summary += f" (warn/crit at {warn:.1f}%/{crit:.1f}%)"

            yield Result(state=state, summary=summary)

            yield Metric(
                name="cpu_utilization",
                value=cpu_percent,
                levels=(warn, crit),
                boundaries=(0, 100)
            )
        else:
            yield Result(state=State.OK, notice="CPU metrics not available")

        if memory_bytes is not None:
            yield Metric(name="memory_usage", value=memory_bytes)
            yield Result(
                state=State.OK,
                notice=f"Memory usage: {memory_bytes / (1024**3):.2f} GB"
            )
        else:
            yield Result(state=State.OK, notice="Memory metrics not available")

        return

    yield Result(state=State.UNKNOWN, summary=f"Node {item} not found in resource data")


agent_section_storagegrid_resources = AgentSection(
    name="storagegrid_resources",
    parse_function=parse_storagegrid_resources,
)

check_plugin_storagegrid_node_resources = CheckPlugin(
    name="storagegrid_node_resources",
    service_name="StorageGRID Node Resources %s",
    discovery_function=discover_storagegrid_node_resources,
    check_function=check_storagegrid_node_resources,
    check_default_parameters={
        'cpu_levels': (80.0, 90.0),
    },
    check_ruleset_name="storagegrid_node_resources",
    sections=["storagegrid_resources"],
)
