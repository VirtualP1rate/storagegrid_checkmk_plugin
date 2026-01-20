#!/usr/bin/env python3
"""
CheckMK Check Plugin for StorageGRID ILM (Information Lifecycle Management)
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


def parse_storagegrid_ilm(string_table: StringTable) -> dict | None:
    """Parse ILM data"""
    if not string_table:
        return None

    try:
        return json.loads(string_table[0][0])
    except (IndexError, json.JSONDecodeError, ValueError):
        return None


def discover_storagegrid_ilm(section: dict) -> DiscoveryResult:
    """Discover ILM service"""
    if section and 'error' not in section:
        yield Service()


def check_storagegrid_ilm(params: dict, section: dict) -> CheckResult:
    """Check ILM metrics"""
    if not section:
        yield Result(state=State.UNKNOWN, summary="No data available")
        return

    if 'error' in section:
        yield Result(state=State.UNKNOWN, summary=f"Error: {section['error']}")
        return

    scan_rate = section.get('scan_rate')
    scan_period_minutes = section.get('scan_period_minutes')
    awaiting_objects = section.get('awaiting_background_objects')

    if scan_rate is not None:
        yield Metric(name="ilm_scan_rate", value=scan_rate)
        yield Result(
            state=State.OK,
            notice=f"ILM scan rate: {scan_rate:.2f} objects/s"
        )

    if scan_period_minutes is not None:
        scan_period_days = scan_period_minutes / (60 * 24)
        yield Metric(name="ilm_scan_period_days", value=scan_period_days)

        # Get thresholds
        warn, crit = params.get('scan_period_levels', (3.0, 7.0))

        # Determine state
        if scan_period_days >= crit:
            state = State.CRIT
        elif scan_period_days >= warn:
            state = State.WARN
        else:
            state = State.OK

        # Build summary
        summary = f"ILM scan period: {scan_period_days:.1f} days"
        if state != State.OK:
            summary += f" (warn/crit at {warn:.1f}/{crit:.1f} days)"

        yield Result(state=state, summary=summary)

        yield Metric(
            name="ilm_scan_period",
            value=scan_period_days,
            levels=(warn, crit)
        )

    if awaiting_objects is not None:
        yield Metric(name="ilm_awaiting_objects", value=awaiting_objects)

        # Get thresholds
        warn, crit = params.get('awaiting_objects_levels', (100000, 1000000))

        # Determine state
        if awaiting_objects >= crit:
            state = State.CRIT
        elif awaiting_objects >= warn:
            state = State.WARN
        else:
            state = State.OK

        # Build summary
        summary = f"Objects awaiting ILM: {int(awaiting_objects):,}"
        if state != State.OK:
            summary += f" (warn/crit at {warn:,}/{crit:,})"

        yield Result(state=state, summary=summary)

        yield Metric(
            name="ilm_queue",
            value=awaiting_objects,
            levels=(warn, crit)
        )


agent_section_storagegrid_ilm = AgentSection(
    name="storagegrid_ilm",
    parse_function=parse_storagegrid_ilm,
)

check_plugin_storagegrid_ilm = CheckPlugin(
    name="storagegrid_ilm",
    service_name="StorageGRID ILM",
    discovery_function=discover_storagegrid_ilm,
    check_function=check_storagegrid_ilm,
    check_default_parameters={
        'scan_period_levels': (3.0, 7.0),
        'awaiting_objects_levels': (100000, 1000000),
    },
    check_ruleset_name="storagegrid_ilm",
    sections=["storagegrid_ilm"],
)
