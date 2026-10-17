"""Download only the selected version from the canonical public Kaggle endpoint."""

import json
import shutil
import tempfile
import zipfile
from pathlib import Path
from urllib.request import Request, urlopen

from payment_risk.contracts import fingerprint, manifest


def download(output: Path) -> Path:
    spec = manifest()
    target = output / spec["filename"]
    if target.exists() or (output / "acquisition.json").exists():
        raise FileExistsError("Acquisition files already exist; use a new output directory.")
    output.mkdir(parents=True, exist_ok=True)
    # Temporary archive never becomes a published artifact. No broad extractall operation.
    with tempfile.TemporaryDirectory(prefix="paysim-download-") as temporary:
        archive = Path(temporary) / "download.zip"
        request = Request(spec["download_url"], headers={"User-Agent": "payment-risk/0.1"})
        print("Downloading canonical PaySim version 2...", flush=True)
        with urlopen(request, timeout=60) as response, archive.open("wb") as stream:
            if response.headers.get_content_type() != "application/zip":
                raise ValueError(
                    "Canonical endpoint did not return a ZIP; no alternate source used."
                )
            shutil.copyfileobj(response, stream, length=1024 * 1024)
        extracted = Path(temporary) / spec["filename"]
        with zipfile.ZipFile(archive) as bundle:
            entries = bundle.infolist()
            if len(entries) != 1 or entries[0].filename != spec["filename"]:
                raise ValueError("Unexpected archive contents; no files extracted.")
            if entries[0].file_size != spec["bytes"]:
                raise ValueError(
                    "Archive's uncompressed file size differs from the source manifest."
                )
            with bundle.open(entries[0]) as source, extracted.open("xb") as destination:
                shutil.copyfileobj(source, destination, length=1024 * 1024)
        observed = fingerprint(extracted)
        if not spec["sha256"] or observed["sha256"] != spec["sha256"]:
            raise ValueError(
                "Downloaded fingerprint differs from the pinned artifact; no CSV published."
            )
        # Publish only a verified file. Refuse to replace an existing file.
        with extracted.open("rb") as source, target.open("xb") as destination:
            try:
                shutil.copyfileobj(source, destination, length=1024 * 1024)
            except OSError:
                target.unlink(missing_ok=True)
                raise
    record = {
        "dataset": spec["dataset"],
        "version": spec["version"],
        "download_url": spec["download_url"],
        "observed": observed,
    }
    (output / "acquisition.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2), flush=True)
    return target
