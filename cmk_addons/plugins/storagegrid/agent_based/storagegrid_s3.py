#!/usr/bin/env python3
"""
CheckMK Check Plugin for StorageGRID S3 Performance
CheckMK 2.4.0 API (agent_based v2)
"""

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    Service,
    Result,
    State,
    Metric,
    check_levels,
    render,
    CheckResult,
    DiscoveryResult,
    StringTable,
)
import json


def parse_storagegrid_s3_performance(string_table: StringTable) -> dict | None:
    """Parse S3 performance data"""
    if not string_table:
        return None

    try:
        return json.loads(string_table[0][0])
    except (IndexError, json.JSONDecodeError, ValueError):
        return None


def discover_storagegrid_s3_performance(section: dict) -> DiscoveryResult:
    """Discover S3 performance service"""
    if section and 'error' not in section:
        yield Service()


def check_storagegrid_s3_performance(params: dict, section: dict) -> CheckResult:
    """Check S3 performance metrics"""
    if not section:
        yield Result(state=State.UNKNOWN, summary="No data available")
        return

    if 'error' in section:
        yield Result(state=State.UNKNOWN, summary=f"Error: {section['error']}")
        return

    successful_rate = section.get('successful_rate')
    failed_rate = section.get('failed_rate')
    error_percent = section.get('error_percent')

    if successful_rate is not None:
        yield Metric(name="successful_request_rate", value=successful_rate)
        yield Result(
            state=State.OK,
            notice=f"Successful requests: {successful_rate:.2f} req/s"
        )

    if failed_rate is not None:
        yield Metric(name="failed_request_rate", value=failed_rate)
        yield Result(
            state=State.OK,
            notice=f"Failed requests: {failed_rate:.2f} req/s"
        )

    if error_percent is not None:
        yield from check_levels(
            value=error_percent,
            levels_upper=params.get('error_rate_levels', (1.0, 5.0)),
            metric_name="error_rate",
            label="Error rate",
            render_func=lambda v: f"{v:.2f}%",
        )

        if successful_rate is not None and failed_rate is not None:
            total_rate = successful_rate + failed_rate
            if total_rate > 0:
                yield Result(
                    state=State.OK,
                    notice=f"Total request rate: {total_rate:.2f} req/s"
                )
    else:
        yield Result(state=State.OK, summary="No S3 traffic detected")


agent_section_storagegrid_s3_performance = AgentSection(
    name="storagegrid_s3_performance",
    parse_function=parse_storagegrid_s3_performance,
)

check_plugin_storagegrid_s3_performance = CheckPlugin(
    name="storagegrid_s3_performance",
    service_name="StorageGRID S3 Performance",
    discovery_function=discover_storagegrid_s3_performance,
    check_function=check_storagegrid_s3_performance,
    check_default_parameters={
        'error_rate_levels': (1.0, 5.0),
    },
    check_ruleset_name="storagegrid_s3_performance",
    sections=["storagegrid_s3_performance"],
)
