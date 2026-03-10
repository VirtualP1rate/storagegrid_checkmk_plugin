#!/usr/bin/env python3
"""
CheckMK Rulesets for StorageGRID Check Parameters
CheckMK 2.4.0 API
"""

from cmk.rulesets.v1 import Title, Help
from cmk.rulesets.v1.form_specs import (
    Dictionary,
    DictElement,
    SimpleLevels,
    LevelDirection,
    Float,
    DefaultValue,
)
from cmk.rulesets.v1.rule_specs import CheckParameters, Topic, HostCondition


def _formspec_s3_performance():
    return Dictionary(
        title=Title("StorageGRID S3 Performance"),
        help_text=Help(
            "Configure warning and critical thresholds for the StorageGRID S3 "
            "error rate. The error rate is the percentage of failed S3 requests "
            "out of all S3 requests in the last 5 minutes."
        ),
        elements={
            "error_rate_levels": DictElement(
                required=False,
                parameter_form=SimpleLevels[float](
                    title=Title("S3 Error Rate"),
                    help_text=Help(
                        "Percentage of S3 requests that returned an error (4xx/5xx). "
                        "Client-side errors such as 404s and permission denials are "
                        "included. Raise these thresholds if your environment generates "
                        "frequent benign client errors."
                    ),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Float(unit_symbol="%"),
                    prefill_fixed_levels=DefaultValue((1.0, 5.0)),
                ),
            ),
        },
    )


rule_spec_storagegrid_s3_performance = CheckParameters(
    name="storagegrid_s3_performance",
    title=Title("StorageGRID S3 Performance"),
    topic=Topic.STORAGE,
    parameter_form=_formspec_s3_performance,
    condition=HostCondition(),
)
