# controlplane-proto

Python distribution of the `spanopticon.v1` ContractEcho protocol. The package
provides `contractecho_pb2`, `contractecho_pb2_grpc`, a typing stub, and the
`controlplane_proto_data/contractecho.proto` resource.

## Development

Requires Python 3.13+ and uv 0.11.26:

```sh
bash scripts/check.sh
```

The script uses locked dependencies, runs the protocol tests, builds a wheel and
source distribution, and repeats tests in a fresh environment outside the checkout
against the wheel and an sdist-rebuilt wheel. Both wheels must contain the exact
runtime and resource files. Tests reject missing resources in installed wheels.

CI runs the same checks on isolated GitHub-hosted Ubuntu workers for pull requests,
main and manual runs, with read-only repository access and pinned actions.
The checks do not publish packages or deploy services.

## Artifact contract evidence

After building a wheel, inspect its exact bytes without importing its code:

```sh
uv run --frozen python scripts/export_release_contract.py dist/controlplane_proto-0.2.0-py3-none-any.whl --output /tmp/proto-contract
```

Use the actual wheel filename and a new output directory. `contract.json` contains
the serialized protobuf descriptor as readable JSON and SHA-256 hashes of every
packaged runtime/resource file. Unknown, missing or duplicate entries are rejected
so added public surfaces cannot silently disappear from coverage. `evidence.json`
binds the contract to the wheel digest and owning package version. The exporter
reads the descriptor literal through Python's AST; it never executes wheel code.

This is intentionally conservative: even generated-code or resource formatting
changes alter the contract. Package version metadata alone does not. The package
check exports both the original wheel and the sdist-rebuilt wheel and requires
identical contract snapshots, alongside the existing installed-wheel tests.
Each fresh installation must also match every captured file digest and the
descriptor exported from the wheel.

Artifact inspection does not establish publisher provenance, semantic equivalence
of generated code and protocol source, consumer compatibility, or an accepted
release baseline. Keep those qualification steps separate. These outputs contain
no acceptance flag or fabricated publication URI, and are not automatically
installed as a release baseline.
## Release channels

Main validation retains its exact qualified files in Actions artifacts. It does
not create GitHub releases or tags. Historical `test-<commit>` prereleases remain
qualification evidence and do not establish an accepted stable release.

Stable publication requires an explicit `vMAJOR.MINOR.PATCH` tag, the exact
successful main validation artifact, compatible declared contracts and an actual
immutable stable baseline. The publisher independently verifies that evidence;
successful caller jobs alone cannot establish acceptance. Missing evidence and
first-stable bootstrap remain closed. Package qualification, coordinated consumer
acceptance and runtime deployment remain separate.


### Actions qualification and stable publication

Main merges and workflow completion do not publish GitHub test releases. Exact
qualification files remain in Actions artifacts with finite retention. The pinned
publisher independently verifies a real immutable stable baseline and refuses
qualification snapshots, even if a caller job reports success. Existing valid
stable records are retained; no release, version change, deployment or human
approval prerequisite is introduced by this correction.
