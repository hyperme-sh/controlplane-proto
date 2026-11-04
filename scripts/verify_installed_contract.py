"""Check a freshly installed wheel against its exported artifact contract."""
import hashlib
import importlib.metadata
import json
from pathlib import Path
import sys

import contractecho_pb2
from google.protobuf import descriptor_pb2, json_format

contract = json.loads(Path(sys.argv[1]).read_text())
distribution = importlib.metadata.distribution('controlplane-proto')
installed = {str(p): p for p in distribution.files}
for name, expected in contract['packaged_file_sha256'].items():
    if name not in installed:
        raise ValueError(f'Missing installed contract file: {name}')
    if hashlib.sha256(installed[name].locate().read_bytes()).hexdigest() != expected:
        raise ValueError(f'Installed contract bytes differ: {name}')
descriptor = descriptor_pb2.FileDescriptorProto.FromString(contractecho_pb2.DESCRIPTOR.serialized_pb)
if json_format.MessageToDict(descriptor, preserving_proto_field_name=True) != contract['protobuf_file_descriptor']:
    raise ValueError('Imported runtime descriptor differs from artifact snapshot')
print('Installed package bytes and runtime descriptor match the wheel contract')
