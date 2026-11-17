"""Protocol validation does not restore retired package publication."""
from pathlib import Path


def test_protocol_checks_do_not_publish_archives():
    root = Path(__file__).resolve().parents[1]
    workflow = (root / ".github/workflows/check.yml").read_text()
    assert not (root / ".github/workflows/release.yml").exists()
    for forbidden in ("upload-artifact", "RELEASE_ARTIFACT_DIR",
                      "packages: write", "docker push"):
        assert forbidden not in workflow
    for required in ("bash scripts/check.sh", "contents: read",
                     "pull_request:", "branches: [main]",
                     "debrunner", "ubuntu-24.04", "cancel-in-progress: true"):
        assert required in workflow
