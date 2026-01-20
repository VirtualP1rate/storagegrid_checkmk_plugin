#!/usr/bin/env python3
"""
CheckMK Check Plugin for StorageGRID Node Health
CheckMK 2.4.0 API (agent_based v2)
"""

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    Service,
    Result,
    State,
    CheckResult,
    DiscoveryResult,
    StringTable,
)
import json


def parse_storagegrid_health(string_table: StringTable) -> dict | None:
    """Parse agent output for health data"""
    if not string_table:
        return None

    try:
        return json.loads(string_table[0][0])
    except (IndexError, json.JSONDecodeError, ValueError):
        return None


def discover_storagegrid_nodes(section: dict) -> DiscoveryResult:
    """Discover services for each node"""
    if not section or 'error' in section:
        return

    for site in section.get('sites', []):
        for node in site.get('nodes', []):
            yield Service(item=f"{site['name']}/{node['name']}")


def check_storagegrid_node(item: str, section: dict) -> CheckResult:
    """Check individual node health"""
    if not section:
        yield Result(state=State.UNKNOWN, summary="No data available")
        return

    if 'error' in section:
        yield Result(state=State.UNKNOWN, summary=f"Error: {section['error']}")
        return

    site_name, node_name = item.split('/', 1)

    for site in section.get('sites', []):
        if site['name'] != site_name:
            continue

        for node in site.get('nodes', []):
            if node['name'] != node_name:
                continue

            node_state = node.get('state', 'unknown')
            severity = node.get('severity', 'unknown')
            node_type = node.get('type', 'unknown')

            if node_state == 'connected' and severity == 'normal':
                yield Result(
                    state=State.OK,
                    summary=f"{node_type} is healthy"
                )
            elif node_state == 'connected' and severity == 'minor':
                yield Result(
                    state=State.WARN,
                    summary=f"{node_type} has minor issues"
                )
            elif node_state == 'administrativelyDown':
                yield Result(
                    state=State.WARN,
                    summary=f"{node_type} is administratively down"
                )
            elif node_state == 'unknown':
                yield Result(
                    state=State.UNKNOWN,
                    summary=f"{node_type} state cannot be determined"
                )
            else:
                yield Result(
                    state=State.CRIT,
                    summary=f"{node_type} state: {node_state}, severity: {severity}"
                )

            return

    yield Result(state=State.UNKNOWN, summary=f"Node {item} not found in monitoring data")


def discover_storagegrid_site(section: dict) -> DiscoveryResult:
    """Discover services for each site"""
    if not section or 'error' in section:
        return

    for site in section.get('sites', []):
        yield Service(item=site['name'])


def check_storagegrid_site(item: str, section: dict) -> CheckResult:
    """Check site health"""
    if not section:
        yield Result(state=State.UNKNOWN, summary="No data available")
        return

    if 'error' in section:
        yield Result(state=State.UNKNOWN, summary=f"Error: {section['error']}")
        return

    for site in section.get('sites', []):
        if site['name'] != item:
            continue

        site_state = site.get('state', 'unknown')
        node_count = len(site.get('nodes', []))

        disconnected_nodes = []
        for node in site.get('nodes', []):
            if node.get('state') != 'connected':
                disconnected_nodes.append(node['name'])

        if site_state == 'connected' and not disconnected_nodes:
            yield Result(
                state=State.OK,
                summary=f"Site operational with {node_count} nodes"
            )
        elif disconnected_nodes:
            yield Result(
                state=State.CRIT,
                summary=f"Site has {len(disconnected_nodes)} disconnected nodes: {', '.join(disconnected_nodes)}"
            )
        else:
            yield Result(
                state=State.WARN,
                summary=f"Site state: {site_state}, {node_count} nodes"
            )

        return

    yield Result(state=State.UNKNOWN, summary=f"Site {item} not found in monitoring data")


agent_section_storagegrid_health = AgentSection(
    name="storagegrid_health",
    parse_function=parse_storagegrid_health,
)

check_plugin_storagegrid_nodes = CheckPlugin(
    name="storagegrid_nodes",
    service_name="StorageGRID Node %s",
    discovery_function=discover_storagegrid_nodes,
    check_function=check_storagegrid_node,
    sections=["storagegrid_health"],
)

check_plugin_storagegrid_sites = CheckPlugin(
    name="storagegrid_sites",
    service_name="StorageGRID Site %s",
    discovery_function=discover_storagegrid_site,
    check_function=check_storagegrid_site,
    sections=["storagegrid_health"],
)
