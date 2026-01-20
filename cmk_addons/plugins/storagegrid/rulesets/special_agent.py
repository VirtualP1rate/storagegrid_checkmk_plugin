#!/usr/bin/env python3
"""
GUI Configuration for StorageGRID Special Agent
CheckMK 2.4.0 API
"""

from cmk.rulesets.v1 import Title, Help
from cmk.rulesets.v1.form_specs import (
    Dictionary,
    DictElement,
    String,
    Password,
    Integer,
    BooleanChoice,
    DefaultValue,
    migrate_to_password,
)
from cmk.rulesets.v1.rule_specs import SpecialAgent, Topic


def _formspec():
    return Dictionary(
        title=Title("NetApp StorageGRID"),
        help_text=Help(
            "This rule configures the special agent for monitoring NetApp StorageGRID "
            "via REST API v4. The agent collects health, capacity, performance, and "
            "alert data from StorageGRID systems."
        ),
        elements={
            "username": DictElement(
                required=True,
                parameter_form=String(
                    title=Title("Grid Admin Username"),
                    help_text=Help("Username for Grid Manager authentication (e.g., 'root')"),
                    prefill=DefaultValue("root"),
                ),
            ),
            "password": DictElement(
                required=True,
                parameter_form=Password(
                    title=Title("Grid Admin Password"),
                    help_text=Help("Password for Grid Manager authentication"),
                    migrate=migrate_to_password,
                ),
            ),
            "no_cert_check": DictElement(
                required=False,
                parameter_form=BooleanChoice(
                    title=Title("Disable SSL certificate verification"),
                    help_text=Help(
                        "Disable SSL certificate verification for self-signed certificates. "
                        "Not recommended for production environments."
                    ),
                    prefill=DefaultValue(False),
                ),
            ),
            "timeout": DictElement(
                required=False,
                parameter_form=Integer(
                    title=Title("Request Timeout"),
                    help_text=Help("Timeout in seconds for API requests"),
                    prefill=DefaultValue(30),
                    custom_validate=(
                        lambda v: None if 5 <= v <= 300
                        else ValueError("Timeout must be between 5 and 300 seconds")
                    ),
                    unit_symbol="seconds",
                ),
            ),
        },
    )


rule_spec_storagegrid = SpecialAgent(
    name="storagegrid",
    title=Title("NetApp StorageGRID"),
    topic=Topic.STORAGE,
    parameter_form=_formspec,
)
