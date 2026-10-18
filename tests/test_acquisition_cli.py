"""Exercise acquisition without network access and test the actual command entrypoint."""

import io
import json
import subprocess
import sys
import zipfile

import pytest

from payment_risk import acquire
from payment_risk.cli import main
from payment_risk.contracts import fingerprint


@pytest.fixture
def fake_download(monkeypatch, make_csv, demo_rows):
    path = make_csv(demo_rows)
    spec = {
        "dataset": "TEST FIXTURE",
        "version": 2,
        "download_url": "https://example.invalid",
        **fingerprint(path),
    }

    def setup(*, member=None, content=None, content_type="application/zip"):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as bundle:
            bundle.writestr(
                member or path.name, content if content is not None else path.read_bytes()
            )

        class Response(io.BytesIO):
            class headers:
                @staticmethod
                def get_content_type():
                    return content_type

        monkeypatch.setattr(acquire, "manifest", lambda: spec)
        monkeypatch.setattr(acquire, "urlopen", lambda *args, **kwargs: Response(buffer.getvalue()))
        return spec

    return setup


def test_download_verifies_before_publishing(fake_download, tmp_path):
    spec = fake_download()
    output = tmp_path / "download"
    target = acquire.download(output)
    assert fingerprint(target)["sha256"] == spec["sha256"]
    record = json.loads((output / "acquisition.json").read_text())
    assert record["observed"] == fingerprint(target)
    with pytest.raises(FileExistsError):
        acquire.download(output)


@pytest.mark.parametrize("kind", ["path", "size", "hash", "html"])
def test_bad_download_is_not_published(kind, fake_download, tmp_path):
    if kind == "path":
        fake_download(member="../not-allowed.csv")
    elif kind == "size":
        fake_download(content=b"bad")
    elif kind == "hash":
        spec = fake_download()
        spec["sha256"] = "0" * 64
    else:
        fake_download(content_type="text/html")
    output = tmp_path / "download"
    with pytest.raises(ValueError):
        acquire.download(output)
    assert not list(output.glob("*.csv"))
    assert not (output / "acquisition.json").exists()


def test_module_entrypoint(tmp_path):
    output = tmp_path / "demo"
    process = subprocess.run(
        [sys.executable, "-m", "payment_risk", "demo", "--output", str(output)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert process.returncode == 0, process.stderr
    assert json.loads((output / "run.json").read_text())["queries_executed"] == 9
    assert "NOT PaySim Results" in (output / "investigation.md").read_text()


def test_cli_refuses_to_overwrite_output(tmp_path, capsys):
    output = tmp_path / "demo"
    assert main(["demo", "--output", str(output)]) == 0
    assert main(["demo", "--output", str(output)]) == 1
    assert "File exists" in capsys.readouterr().err


def test_cli_validation_failure_has_nonzero_exit(tmp_path, make_csv, demo_rows):
    assert main(["run", "--csv", str(make_csv(demo_rows)), "--output", str(tmp_path / "bad")]) == 2


@pytest.mark.parametrize(
    "arguments",
    [
        ["--minimum-amount", "NaN"],
        ["--minimum-amount", "abc"],
        ["--minimum-amount", "-1"],
        ["--limit", "0"],
    ],
)
def test_cli_invalid_parameters_leave_no_output(arguments, tmp_path):
    output = tmp_path / "demo"
    assert main(["demo", "--output", str(output), *arguments]) == 1
    assert not output.exists()
