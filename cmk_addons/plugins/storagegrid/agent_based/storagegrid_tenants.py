#!/usr/bin/env python3
"""
CheckMK Check Plugin for StorageGRID Tenant Usage
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
    render,
    CheckResult,
    DiscoveryResult,
    StringTable,
)


def parse_storagegrid_tenant_usage(string_table: StringTable) -> dict | None:
    """Parse tenant usage data"""
    if not string_table:
        return None

    try:
        return json.loads(string_table[0][0])
    except (IndexError, json.JSONDecodeError, ValueError):
        return None


def discover_storagegrid_tenant_usage(section: dict) -> DiscoveryResult:
    """Discover tenant usage services"""
    if not section or 'error' in section:
        return

    for tenant in section.get('tenants', []):
        tenant_name = tenant.get('account_name')
        if tenant_name:
            yield Service(item=tenant_name)


def check_storagegrid_tenant_usage(item: str, params: dict, section: dict) -> CheckResult:
    """Check tenant storage usage"""
    if not section:
        yield Result(state=State.UNKNOWN, summary="No data available")
        return

    if 'error' in section:
        yield Result(state=State.UNKNOWN, summary=f"Error: {section['error']}")
        return

    for tenant in section.get('tenants', []):
        if tenant.get('account_name') != item:
            continue

        data_bytes = tenant.get('data_bytes', 0)
        quota_bytes = tenant.get('quota_bytes', 0)
        quota_percent = tenant.get('quota_percent', 0)
        object_count = tenant.get('object_count', 0)

        yield Metric(name="data_bytes", value=data_bytes, boundaries=(0, quota_bytes) if quota_bytes > 0 else None)
        yield Metric(name="object_count", value=object_count)

        if quota_bytes > 0:
            # Get thresholds
            warn, crit = params.get('quota_levels', (80.0, 90.0))

            # Determine state
            if quota_percent >= crit:
                state = State.CRIT
            elif quota_percent >= warn:
                state = State.WARN
            else:
                state = State.OK

            # Build summary with object count
            summary = f"Quota usage: {quota_percent:.2f}%, {object_count:,} objects"
            if state != State.OK:
                summary += f" (warn/crit at {warn:.1f}%/{crit:.1f}%)"

            yield Result(state=state, summary=summary)

            yield Metric(
                name="quota_utilization",
                value=quota_percent,
                levels=(warn, crit),
                boundaries=(0, 100)
            )

            yield Result(
                state=State.OK,
                notice=f"Used: {render.bytes(data_bytes)} / {render.bytes(quota_bytes)}"
            )
        else:
            yield Result(
                state=State.OK,
                summary=f"Used: {render.bytes(data_bytes)}, {object_count:,} objects (no quota set)"
            )

        return

    yield Result(state=State.UNKNOWN, summary=f"Tenant {item} not found in usage data")


agent_section_storagegrid_tenant_usage = AgentSection(
    name="storagegrid_tenant_usage",
    parse_function=parse_storagegrid_tenant_usage,
)

check_plugin_storagegrid_tenant_usage = CheckPlugin(
    name="storagegrid_tenant_usage",
    service_name="StorageGRID Tenant %s",
    discovery_function=discover_storagegrid_tenant_usage,
    check_function=check_storagegrid_tenant_usage,
    check_default_parameters={
        'quota_levels': (80.0, 90.0),
    },
    check_ruleset_name="storagegrid_tenant_usage",
    sections=["storagegrid_tenant_usage"],
)
