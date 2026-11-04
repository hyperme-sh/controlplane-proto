import json
import pytest
from pathlib import Path
import importlib.metadata
import contractecho_pb2 as pb
import contractecho_pb2_grpc

def test_published_descriptor_and_roundtrip():
    assert pb.DESCRIPTOR.package == "spanopticon.v1"
    assert set(pb.DESCRIPTOR.services_by_name) == {"ContractEcho"}
    original = pb.UserWire(id="u", email="u@example.com", display_name="User")
    restored = pb.UserWire.FromString(original.SerializeToString())
    assert original == restored
    assert not restored.HasField("tenant_id")
    original.tenant_id = "tenant"
    assert pb.UserWire.FromString(original.SerializeToString()).HasField("tenant_id")

def test_protocol_source_is_shipped():
    distribution=importlib.metadata.distribution("controlplane-proto")
    paths=[p for p in distribution.files if str(p).endswith("controlplane_proto_data/contractecho.proto")]
    # Editable source checks validate the original file; wheel checks require the packaged resource.
    metadata = json.loads(distribution.read_text("direct_url.json") or "{}")
    if metadata.get("dir_info", {}).get("editable") is True and not paths:
        assert (Path(__file__).resolve().parents[1]/"proto/spanopticon/v1/contractecho.proto").is_file()
    else:
        assert len(paths)==1
        assert 'package spanopticon.v1;' in paths[0].locate().read_text()


@pytest.mark.parametrize("metadata", [
    {"url": "file:///tmp/package.whl", "archive_info": {}},
    {"url": "file:///tmp/source", "dir_info": {"editable": False}},
])
def test_noneditable_missing_resource_is_rejected(monkeypatch, metadata):
    class MissingResource:
        files = []
        def read_text(self, name):
            return json.dumps(metadata)
    monkeypatch.setattr(importlib.metadata, "distribution", lambda name: MissingResource())
    with pytest.raises(AssertionError):
        test_protocol_source_is_shipped()
