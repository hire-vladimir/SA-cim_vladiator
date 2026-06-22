"""Regression tests for lookups/cim_validator_field_regex.csv integrity."""

import csv
import re
from pathlib import Path

LOOKUP_PATH = Path(__file__).resolve().parent.parent / "lookups" / "cim_validator_field_regex.csv"

CANONICAL_DATAMODEL = "UBA_Endpoint_Filesystem"
CANONICAL_FIELD = "alarmCategories"

TRUNCATED_DATAMODELS = [
    "UBA_Endpoint_Port",
    "UBA_Endpoint_Processes",
    "UBA_Endpoint_Registry",
    "UBA_Endpoint_Services",
    "UBA_External_Alarm",
    "UBA_IDS_IPS",
]


def _load_rows():
    with LOOKUP_PATH.open(newline="") as handle:
        return list(csv.reader(handle))


def _load_dict_rows():
    with LOOKUP_PATH.open(newline="") as handle:
        return list(csv.DictReader(handle))


def test_lookup_csv_has_three_columns_on_every_row():
    for row in _load_rows():
        assert len(row) == 3, f"Expected 3 columns, got {len(row)}: {row[:1]}"


def test_all_validation_regex_values_compile():
    failures = []
    for row in _load_dict_rows():
        pattern = row["validation_regex"]
        try:
            re.compile(pattern)
        except re.error as exc:
            failures.append(f"{row['datamodel']}/{row['field']}: {exc}")
    assert not failures, "Regex compile failures:\n" + "\n".join(failures)


def test_truncated_alarm_categories_match_canonical_pattern():
    rows = {
        (row["datamodel"], row["field"]): row["validation_regex"]
        for row in _load_dict_rows()
    }
    canonical = rows[(CANONICAL_DATAMODEL, CANONICAL_FIELD)]

    mismatches = []
    for datamodel in TRUNCATED_DATAMODELS:
        actual = rows[(datamodel, CANONICAL_FIELD)]
        if actual != canonical:
            mismatches.append(
                f"{datamodel}: length {len(actual)} != canonical {len(canonical)}"
            )

    assert not mismatches, "Truncated alarmCategories rows differ from canonical:\n" + "\n".join(
        mismatches
    )


def test_canonical_alarm_categories_rows_unchanged_and_compile():
    rows = {
        (row["datamodel"], row["field"]): row["validation_regex"]
        for row in _load_dict_rows()
    }
    for datamodel in (CANONICAL_DATAMODEL, "UBA_Host AV"):
        pattern = rows[(datamodel, CANONICAL_FIELD)]
        assert pattern.startswith(r"\b(?:")
        re.compile(pattern)