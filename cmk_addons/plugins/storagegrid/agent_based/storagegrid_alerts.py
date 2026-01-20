#!/usr/bin/env python3
"""
CheckMK Check Plugin for StorageGRID Alerts
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


def parse_storagegrid_alerts(string_table: StringTable) -> dict | None:
    """Parse alerts data"""
    if not string_table:
        return None

    try:
        return json.loads(string_table[0][0])
    except (IndexError, json.JSONDecodeError, ValueError):
        return None


def discover_storagegrid_alerts(section: dict) -> DiscoveryResult:
    """Discover alert summary service"""
    if section and 'error' not in section:
        yield Service()


def check_storagegrid_alerts(section: dict) -> CheckResult:
    """Check active alerts summary"""
    if not section:
        yield Result(state=State.UNKNOWN, summary="No data available")
        return

    if 'error' in section:
        yield Result(state=State.UNKNOWN, summary=f"Error: {section['error']}")
        return

    alerts = section.get('alerts', [])

    critical_alerts = [a for a in alerts if a.get('severity') == 'critical']
    major_alerts = [a for a in alerts if a.get('severity') == 'major']
    minor_alerts = [a for a in alerts if a.get('severity') == 'minor']

    total_alerts = len(alerts)

    yield Metric(name="critical_alerts", value=len(critical_alerts))
    yield Metric(name="major_alerts", value=len(major_alerts))
    yield Metric(name="minor_alerts", value=len(minor_alerts))
    yield Metric(name="total_alerts", value=total_alerts)

    if critical_alerts:
        alert_names = ', '.join(set(a['name'] for a in critical_alerts[:3]))
        if len(critical_alerts) > 3:
            alert_names += f" and {len(critical_alerts) - 3} more"
        yield Result(
            state=State.CRIT,
            summary=f"{len(critical_alerts)} critical alert(s): {alert_names}"
        )

    if major_alerts:
        alert_names = ', '.join(set(a['name'] for a in major_alerts[:3]))
        if len(major_alerts) > 3:
            alert_names += f" and {len(major_alerts) - 3} more"
        yield Result(
            state=State.WARN,
            summary=f"{len(major_alerts)} major alert(s): {alert_names}"
        )

    if minor_alerts:
        yield Result(
            state=State.OK,
            notice=f"{len(minor_alerts)} minor alert(s) active"
        )

    if not alerts:
        yield Result(state=State.OK, summary="No active alerts")


agent_section_storagegrid_alerts = AgentSection(
    name="storagegrid_alerts",
    parse_function=parse_storagegrid_alerts,
)

check_plugin_storagegrid_alerts = CheckPlugin(
    name="storagegrid_alerts",
    service_name="StorageGRID Alerts Summary",
    discovery_function=discover_storagegrid_alerts,
    check_function=check_storagegrid_alerts,
    sections=["storagegrid_alerts"],
)
