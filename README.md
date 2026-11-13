# controlplane-proto

Python package for the `spanopticon.v1` ContractEcho protocol buffers. Version
**0.2.0** in this tree installs `contractecho_pb2`, `contractecho_pb2_grpc`, the
`contractecho_pb2.pyi` typing stub, and the
`controlplane_proto_data/contractecho.proto` resource. It targets Python 3.13+
and depends on `protobuf>=6.33.6` and `grpcio>=1.80.0`.

## Why

Hypermesh control-plane services hand each other three records on a lease: the
marketplace listing a host offers, the token-usage row that meters a renter's
model call, and the shared user those records point at. Those shapes live as
Python models in Spanopticon (`Listing`, `TokenUsage`, `SharedUser`). This
package is the protobuf encoding of those three records, so callers
serialize one shared descriptor.

## How it works

The schema is `proto/spanopticon/v1/contractecho.proto`, package
`spanopticon.v1`. `ContractEcho` has three unary RPCs. Each one takes a message
and returns that same message: `EchoListing`, `EchoTokenUsage`, and `EchoUser`.
The schema comment describes them as identity echoes kept so code generation
emits a descriptor and stubs for the messages. Callers use the message types.

| Message | Model it encodes | What the bytes carry |
| --- | --- | --- |
| `ListingWire` | `spanopticon_models.marketplace.Listing` | Listing id, tenant, seller (the host), title, description, listing type, price type, optional integer price amount, optional SKU, and metadata as a JSON string |
| `TokenUsageWire` | `spanopticon_models.ai_metering.TokenUsage` | User, tenant, model name, input and output token counts, cost as a decimal string, and a `google.protobuf.Timestamp` |
| `UserWire` | `spanopticon_models.user.SharedUser` | User id, email, display name, and an optional tenant id |

Generated sources are checked in under `src/` and mapped to the wheel root.
The wheel also force-includes the `.proto` at
`controlplane_proto_data/contractecho.proto`. `proto/buf.yaml` is a Buf module
(`buf.build/local/spanopticon`) with the Google common protos, `DEFAULT` lint,
and `FILE` breaking checks.

RPC paths:

- `/spanopticon.v1.ContractEcho/EchoListing`
- `/spanopticon.v1.ContractEcho/EchoTokenUsage`
- `/spanopticon.v1.ContractEcho/EchoUser`

## Practical use

The package is not on PyPI. Install from a checkout of this repository, or from
a wheel attached to a GitHub release.

Development checkout (package **0.2.0**). Requires Python 3.13+ and
[uv](https://docs.astral.sh/uv/) 0.11.26:

```sh
git clone https://github.com/hyperme-sh/controlplane-proto.git
cd controlplane-proto
uv sync --frozen
```

Stable release wheel (package **0.24.0**, tag `v0.24.0`):

```sh
python3.13 -m venv .venv
. .venv/bin/activate
pip install \
  "https://github.com/hyperme-sh/controlplane-proto/releases/download/v0.24.0/controlplane_proto-0.24.0-py3-none-any.whl"
```

`pip` reads `Requires-Dist` from the wheel and installs `protobuf` and `grpcio`.
Import the generated modules and serialize the messages:

```python
from datetime import datetime, timezone

import contractecho_pb2 as pb

listing = pb.ListingWire(
    id="listing-1",
    tenant_id="tenant-1",
    seller_id="host-1",
    title="One GPU hour",
    description="Capacity offered by a host",
    listing_type="gpu_hour",
    price_type="fixed",
    price_amount=250,
    metadata_json='{"gpu":"example"}',
    sku="gpu-1h",
)
raw = listing.SerializeToString()
assert pb.ListingWire.FromString(raw) == listing

usage = pb.TokenUsageWire(
    user_id="user-1",
    tenant_id="tenant-1",
    model="example-model",
    input_tokens=128,
    output_tokens=64,
    cost_usd="0.0123",
)
usage.timestamp.FromDatetime(datetime.now(timezone.utc))
assert pb.TokenUsageWire.FromString(usage.SerializeToString()) == usage

user = pb.UserWire(id="user-1", email="user@example.com", display_name="User")
assert not user.HasField("tenant_id")
user.tenant_id = "tenant-1"
assert pb.UserWire.FromString(user.SerializeToString()).HasField("tenant_id")
```

`listing_type`, `price_type`, and `metadata_json` are caller-defined strings.
`cost_usd` is a decimal string such as `"0.0123"`.

The installed distribution also ships the schema. From a non-editable install:

```python
import importlib.metadata

dist = importlib.metadata.distribution("controlplane-proto")
proto = next(
    path for path in dist.files
    if str(path).endswith("controlplane_proto_data/contractecho.proto")
)
text = proto.locate().read_text()
assert "package spanopticon.v1;" in text
```

`contractecho_pb2_grpc` provides `ContractEchoStub` and `ContractEchoServicer`
for the three echo methods. The generated servicer methods are unimplemented
until a process fills them in. An identity implementation returns the request
object.

## How Hypermesh uses it

Hypermesh renters take capacity that hosts offer. The control plane is the
service path for that lease: it records the host's marketplace listing, the
renter's identity, and the metered model use that follows.

This package is the Python wire format for those three records.

- A host offer is a `ListingWire`. `seller_id` is the host, `tenant_id` is the
  tenant the listing belongs to, and `price_amount` plus `price_type` are the
  offer. `metadata_json` carries the extra listing document as JSON text.
- A renter account on that listing is a `UserWire` (`id`, `email`,
  `display_name`, optional `tenant_id`).
- Metered model traffic after the lease is a `TokenUsageWire`: which user and
  tenant, which model, input and output token counts, and `cost_usd`.

Control-plane Python code that uses the Spanopticon model classes imports
`contractecho_pb2` and exchanges those serialized bytes. `ContractEcho` stays
in the schema so the descriptor, the stubs, and the packaged `.proto` all name
the same three messages.

## Develop and test

From a checkout, with Python 3.13+ and uv 0.11.26:

```sh
bash scripts/check.sh
```

The script syncs the locked environment, runs `tests/` and `tests_tools/`,
builds a wheel and a source distribution, and repeats the protocol tests in a
fresh environment outside the checkout against that wheel and against a wheel
rebuilt from the sdist. Both wheels must contain the same runtime modules and
the packaged `.proto`. Installed wheels without that resource fail the test.

Optional schema lint, from `proto/` after `buf dep update`:

```sh
buf lint
```

To dump the contract of a built wheel without importing it:

```sh
uv build --no-sources --out-dir dist
uv run --frozen python scripts/export_release_contract.py \
  dist/controlplane_proto-0.2.0-py3-none-any.whl \
  --output /tmp/proto-contract
```

Use the wheel filename you actually built and a new output directory.
`contract.json` is the serialized file descriptor as JSON plus the SHA-256 of
every packaged runtime and resource file. `evidence.json` binds that contract
to the wheel digest and the package version. The exporter reads the descriptor
literal from the generated file's syntax tree. Unknown, missing, or duplicate
wheel entries are rejected. What that snapshot qualifies is described in
[docs/releasing.md](docs/releasing.md).

GitHub Actions runs `bash scripts/check.sh` on pull requests, on `main`, and on
manual runs (`.github/workflows/check.yml`). The job checks out the repo
read-only and uses pinned actions. On this public repository the job runs on
`ubuntu-24.04`. A release is published only by the workflows in
[docs/releasing.md](docs/releasing.md), and only from a retained main artifact.

## Release and versioning

This checkout's installable version is **0.2.0**. The stable GitHub release is
[`v0.24.0`](https://github.com/hyperme-sh/controlplane-proto/releases/tag/v0.24.0)
(`controlplane_proto-0.24.0`). Automatic package prereleases are not
published. Tags and the records under `releases/` are documented in
[docs/releasing.md](docs/releasing.md).

## License

Apache-2.0. The text is [`LICENSE`](LICENSE) and is included in wheels and
source distributions.
