#!/usr/bin/env python3
"""
Server-side configuration for StorageGRID Special Agent
Defines how CheckMK calls the special agent
CheckMK 2.4.0 API
"""

from collections.abc import Iterator
from typing import Any

from pydantic import BaseModel

from cmk.server_side_calls.v1 import (
    HostConfig,
    Secret,
    SpecialAgentCommand,
    SpecialAgentConfig,
)


class Params(BaseModel):
    """Parameters for StorageGRID special agent"""
    username: str
    password: Secret
    no_cert_check: bool | None = None
    timeout: int | None = None


def _agent_storagegrid_arguments(
    params: Params,
    host_config: HostConfig,
) -> Iterator[SpecialAgentCommand]:
    """Build command line arguments for the special agent"""
    
    args: list[str] = []
    
    # Hostname - use the host's name or IP
    args.extend(["--hostname", host_config.name])
    
    # Username
    args.extend(["--username", params.username])
    
    # Password - extract from Secret object
    args.extend(["--password", params.password.unsafe()])
    
    # SSL certificate check
    if params.no_cert_check:
        args.append("--no-cert-check")
    
    # Timeout
    if params.timeout is not None:
        args.extend(["--timeout", str(params.timeout)])
    
    yield SpecialAgentCommand(command_arguments=args)


special_agent_storagegrid = SpecialAgentConfig(
    name="storagegrid",
    parameter_parser=Params.model_validate,
    commands_function=_agent_storagegrid_arguments,
)
