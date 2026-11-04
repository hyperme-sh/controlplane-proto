"""Export conservative contract evidence from a wheel without executing its code."""
import argparse
import ast
import email.parser
import hashlib
import io
import json
from pathlib import Path
import re
import zipfile

from google.protobuf import descriptor_pb2, json_format

RUNTIME = {
    'contractecho_pb2.py', 'contractecho_pb2.pyi', 'contractecho_pb2_grpc.py',
    'controlplane_proto_data/contractecho.proto',
}


def snapshot(wheel):
    # Hash and inspect the same bytes, even if the path is replaced concurrently.
    raw = Path(wheel).read_bytes()
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError('Duplicate wheel entries')
        metadata_files = [n for n in names if re.fullmatch(r'controlplane_proto-[^/]+\.dist-info/METADATA', n)]
        if len(metadata_files) != 1:
            raise ValueError('Expected exactly one owning distribution')
        prefix = metadata_files[0].removesuffix('METADATA')
        if {n for n in names if not n.startswith(prefix)} != RUNTIME:
            raise ValueError('Unexpected or missing wheel contents; review contract coverage')
        metadata = email.parser.BytesParser().parsebytes(archive.read(metadata_files[0]))
        if metadata.get_all('Name') != ['controlplane-proto']:
            raise ValueError('Wrong or ambiguous distribution identity')
        versions = metadata.get_all('Version', [])
        if len(versions) != 1 or not re.fullmatch(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)', versions[0]):
            raise ValueError('Expected one stable semantic version')
        if prefix != f'controlplane_proto-{versions[0]}.dist-info/':
            raise ValueError('Distribution directory and metadata version differ')
        contents = {n: archive.read(n) for n in sorted(RUNTIME)}
    tree = ast.parse(contents['contractecho_pb2.py'])
    assignments = [n for n in tree.body if isinstance(n, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == 'DESCRIPTOR' for t in n.targets)]
    if len(assignments) != 1:
        raise ValueError('Expected one generated DESCRIPTOR assignment')
    call = assignments[0].value
    if (not isinstance(call, ast.Call) or not isinstance(call.func, ast.Attribute)
            or call.func.attr != 'AddSerializedFile' or len(call.args) != 1 or call.keywords
            or not isinstance(call.args[0], ast.Constant) or not isinstance(call.args[0].value, bytes)):
        raise ValueError('Expected a literal serialized descriptor; execution is forbidden')
    descriptor = descriptor_pb2.FileDescriptorProto.FromString(call.args[0].value)
    if descriptor.name != 'contractecho.proto' or descriptor.package != 'spanopticon.v1' or not descriptor.service:
        raise ValueError('Wrong or empty protocol descriptor')
    contract = {
        'schema_version': 1,
        'coverage': 'conservative complete packaged runtime and protocol resources',
        'protobuf_file_descriptor': json_format.MessageToDict(descriptor, preserving_proto_field_name=True),
        'packaged_file_sha256': {n: hashlib.sha256(data).hexdigest() for n, data in contents.items()},
    }
    encoded = (json.dumps(contract, sort_keys=True, indent=2) + '\n').encode()
    evidence = {'schema_version': 1, 'distribution': 'controlplane-proto', 'version': versions[0],
                'wheel_sha256': hashlib.sha256(raw).hexdigest(), 'wheel_size': len(raw),
                'contract_sha256': hashlib.sha256(encoded).hexdigest(),
                'qualification': 'artifact inspection only; not accepted release or consumer qualification'}
    return encoded, evidence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('wheel', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    # Validate before creating output; never replace an existing evidence directory.
    contract, evidence = snapshot(args.wheel)
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / 'contract.json').write_bytes(contract)
    (args.output / 'evidence.json').write_text(json.dumps(evidence, sort_keys=True, indent=2) + '\n')


if __name__ == '__main__':
    main()
