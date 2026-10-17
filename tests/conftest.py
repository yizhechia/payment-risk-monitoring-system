"""Small, deliberately constructed examples; never presented as PaySim observations."""

import csv
from importlib.resources import files

import pytest

from payment_risk.contracts import COLUMNS
from payment_risk.pipeline import ingest


@pytest.fixture
def demo_rows():
    with files("payment_risk").joinpath("demo.csv").open() as stream:
        return list(csv.DictReader(stream))


@pytest.fixture
def make_csv(tmp_path):
    def write(rows, name="input.csv", columns=COLUMNS):
        path = tmp_path / name
        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)
        return path

    return write


@pytest.fixture
def demo_run(tmp_path, make_csv, demo_rows):
    output = tmp_path / "validated"
    validation = ingest(make_csv(demo_rows), output, canonical=False)
    return output, validation
