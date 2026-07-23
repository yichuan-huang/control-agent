import hashlib
from pathlib import Path
import tomllib


ROOT = Path(__file__).resolve().parents[1]
AGPL_V3_SHA256 = "8486a10c4393cee1c25392769ddd3b2d6c242d6ec7928e1414efff7dfb2f07ef"


def test_root_license_is_canonical_agpl_v3_text():
    license_bytes = (ROOT / "LICENSE").read_bytes()

    assert hashlib.sha256(license_bytes).hexdigest() == AGPL_V3_SHA256
    assert license_bytes.splitlines()[0] == (
        b"                    GNU AFFERO GENERAL PUBLIC LICENSE"
    )
    assert license_bytes.endswith(b"\n")
    assert b"Version 3, 19 November 2007" in license_bytes
    assert license_bytes.count(b"https://www.gnu.org/licenses/") == 2
    assert b"http://www.gnu.org/licenses/" not in license_bytes
    assert b"https://fsf.org/" in license_bytes
    assert b"http://fsf.org/" not in license_bytes


def test_pyproject_declares_agpl_v3_only_with_copyright_holder():
    with (ROOT / "pyproject.toml").open("rb") as handle:
        metadata = tomllib.load(handle)

    assert metadata["build-system"]["requires"] == ["setuptools>=77.0.3"]
    assert metadata["project"]["authors"] == [{"name": "Yichuan Huang"}]
    assert metadata["project"]["license"] == "AGPL-3.0-only"
    assert metadata["project"]["license-files"] == ["LICENSE"]
    assert metadata["project"]["urls"]["Repository"] == (
        "https://github.com/yichuan-huang/control-agent"
    )
