#!/usr/bin/env python3
"""
CheckMK Check Plugin for StorageGRID Storage Capacity
CheckMK 2.4.0 API (agent_based v2)
Split into separate data and metadata checks for independent alerting
"""

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
import json


def parse_storagegrid_capacity(string_table: StringTable) -> dict | None:
    """Parse capacity data"""
    if not string_table:
        return None

    try:
        return json.loads(string_table[0][0])
    except (IndexError, json.JSONDecodeError, ValueError):
        return None


def discover_storagegrid_data_capacity(section: dict) -> DiscoveryResult:
    """Discover data capacity service"""
    if section and 'error' not in section and section.get('data_bytes') is not None:
        yield Service()


def check_storagegrid_data_capacity(params: dict, section: dict) -> CheckResult:
    """Check data storage capacity"""
    if not section:
        yield Result(state=State.UNKNOWN, summary="No data available")
        return

    if 'error' in section:
        yield Result(state=State.UNKNOWN, summary=f"Error: {section['error']}")
        return

    data_bytes = section.get('data_bytes')
    usable_bytes = section.get('usable_space_bytes')
    data_percent = section.get('data_percent')

    if data_bytes is not None and usable_bytes is not None and data_percent is not None:
        # Get thresholds
        warn, crit = params.get('data_levels', (80.0, 90.0))
        
        # Determine state
        if data_percent >= crit:
            state = State.CRIT
        elif data_percent >= warn:
            state = State.WARN
        else:
            state = State.OK
        
        # Build summary
        summary = f"Data capacity: {data_percent:.2f}%"
        if state != State.OK:
            summary += f" (warn/crit at {warn:.1f}%/{crit:.1f}%)"
        
        yield Result(state=state, summary=summary)
        
        yield Metric(
            name="data_utilization",
            value=data_percent,
            levels=(warn, crit),
            boundaries=(0, 100)
        )
        
        yield Metric(
            name="data_bytes",
            value=data_bytes,
            boundaries=(0, usable_bytes)
        )

        yield Result(
            state=State.OK,
            notice=f"Used: {render.bytes(data_bytes)} / {render.bytes(usable_bytes)}"
        )
    else:
        yield Result(state=State.UNKNOWN, summary="Data capacity metrics not available")


def discover_storagegrid_metadata_capacity(section: dict) -> DiscoveryResult:
    """Discover metadata capacity service"""
    if section and 'error' not in section and section.get('metadata_bytes') is not None:
        yield Service()


def check_storagegrid_metadata_capacity(params: dict, section: dict) -> CheckResult:
    """Check metadata storage capacity"""
    if not section:
        yield Result(state=State.UNKNOWN, summary="No data available")
        return

    if 'error' in section:
        yield Result(state=State.UNKNOWN, summary=f"Error: {section['error']}")
        return

    metadata_bytes = section.get('metadata_bytes')
    metadata_allowed = section.get('metadata_allowed_bytes')
    metadata_percent = section.get('metadata_percent')

    if metadata_bytes is not None and metadata_allowed is not None and metadata_percent is not None:
        # Get thresholds
        warn, crit = params.get('metadata_levels', (70.0, 80.0))
        
        # Determine state
        if metadata_percent >= crit:
            state = State.CRIT
        elif metadata_percent >= warn:
            state = State.WARN
        else:
            state = State.OK
        
        # Build summary
        summary = f"Metadata capacity: {metadata_percent:.2f}%"
        if state != State.OK:
            summary += f" (warn/crit at {warn:.1f}%/{crit:.1f}%)"
        
        yield Result(state=state, summary=summary)
        
        yield Metric(
            name="metadata_utilization",
            value=metadata_percent,
            levels=(warn, crit),
            boundaries=(0, 100)
        )
        
        yield Metric(
            name="metadata_bytes",
            value=metadata_bytes,
            boundaries=(0, metadata_allowed)
        )

        yield Result(
            state=State.OK,
            notice=f"Metadata used: {render.bytes(metadata_bytes)} / {render.bytes(metadata_allowed)}"
        )
    else:
        yield Result(state=State.UNKNOWN, summary="Metadata capacity metrics not available")


agent_section_storagegrid_capacity = AgentSection(
    name="storagegrid_capacity",
    parse_function=parse_storagegrid_capacity,
)

check_plugin_storagegrid_data_capacity = CheckPlugin(
    name="storagegrid_data_capacity",
    service_name="StorageGRID Data Capacity",
    discovery_function=discover_storagegrid_data_capacity,
    check_function=check_storagegrid_data_capacity,
    check_default_parameters={
        'data_levels': (80.0, 90.0),
    },
    check_ruleset_name="storagegrid_data_capacity",
    sections=["storagegrid_capacity"],
)

check_plugin_storagegrid_metadata_capacity = CheckPlugin(
    name="storagegrid_metadata_capacity",
    service_name="StorageGRID Metadata Capacity",
    discovery_function=discover_storagegrid_metadata_capacity,
    check_function=check_storagegrid_metadata_capacity,
    check_default_parameters={
        'metadata_levels': (70.0, 80.0),
    },
    check_ruleset_name="storagegrid_metadata_capacity",
    sections=["storagegrid_capacity"],
)
