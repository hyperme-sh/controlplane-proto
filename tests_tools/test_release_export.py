import hashlib
import importlib.util
import json
from pathlib import Path
import zipfile

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('export_release_contract', ROOT / 'scripts/export_release_contract.py')
exporter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exporter)


def wheel(tmp_path, version='0.2.0', change=None):
    files = {n: (ROOT / 'src' / n).read_bytes() for n in exporter.RUNTIME if '/' not in n}
    files['controlplane_proto_data/contractecho.proto'] = (ROOT / 'proto/spanopticon/v1/contractecho.proto').read_bytes()
    files[f'controlplane_proto-{version}.dist-info/METADATA'] = f'Name: controlplane-proto\nVersion: {version}\n'.encode()
    if change:
        change(files)
    path = tmp_path / 'artifact.whl'
    with zipfile.ZipFile(path, 'w') as archive:
        for name, data in files.items():
            archive.writestr(name, data)
    return path


def test_binds_exact_bytes_and_exports_descriptor(tmp_path):
    path = wheel(tmp_path)
    contract, evidence = exporter.snapshot(path)
    document = json.loads(contract)
    assert document['protobuf_file_descriptor']['package'] == 'spanopticon.v1'
    assert document['protobuf_file_descriptor']['service'][0]['name'] == 'ContractEcho'
    assert set(document['packaged_file_sha256']) == exporter.RUNTIME
    assert evidence['wheel_sha256'] == hashlib.sha256(path.read_bytes()).hexdigest()
    assert evidence['contract_sha256'] == hashlib.sha256(contract).hexdigest()
    assert exporter.snapshot(path) == (contract, evidence)


def test_package_patch_metadata_does_not_change_contract(tmp_path):
    first, _ = exporter.snapshot(wheel(tmp_path))
    second, evidence = exporter.snapshot(wheel(tmp_path, version='0.2.1'))
    assert first == second
    assert evidence['version'] == '0.2.1'


@pytest.mark.parametrize('mutation', [
    lambda f: f.pop('contractecho_pb2.pyi'),
    lambda f: f.update({'unexpected.py': b'new public surface'}),
    lambda f: f.update({'other-1.dist-info/METADATA': b'Name: other'}),
    lambda f: f.update({'controlplane_proto-0.2.0.dist-info/METADATA': b'Name: other\nVersion: 0.2.0\n'}),
])
def test_rejects_omitted_or_unowned_contents(tmp_path, mutation):
    with pytest.raises(ValueError):
        exporter.snapshot(wheel(tmp_path, change=mutation))


def test_does_not_execute_generated_code(tmp_path):
    sentinel = tmp_path / 'executed'
    def inject(files):
        files['contractecho_pb2.py'] += f'\nopen({str(sentinel)!r}, "w").write("bad")\n'.encode()
    path = wheel(tmp_path, change=inject)
    exporter.snapshot(path)
    assert not sentinel.exists()


def test_rejects_dynamic_descriptor(tmp_path):
    def mutate(files):
        files['contractecho_pb2.py'] = b'DESCRIPTOR = build_descriptor()\n'
    with pytest.raises(ValueError, match='literal'):
        exporter.snapshot(wheel(tmp_path, change=mutate))


def test_contract_detects_runtime_and_resource_changes(tmp_path):
    first, _ = exporter.snapshot(wheel(tmp_path))
    def mutate(files):
        files['contractecho_pb2_grpc.py'] += b'\n# changed generator output\n'
    second, _ = exporter.snapshot(wheel(tmp_path, change=mutate))
    assert first != second


def test_rejects_duplicate_entries(tmp_path):
    path = wheel(tmp_path)
    with pytest.warns(UserWarning), zipfile.ZipFile(path, 'a') as archive:
        archive.writestr('contractecho_pb2.py', b'DESCRIPTOR = None')
    with pytest.raises(ValueError, match='Duplicate'):
        exporter.snapshot(path)
