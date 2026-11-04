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

Successful main-push validation retains the validated Python wheel and source distribution and publishes
an immutable `test-<commit>` GitHub prerelease. Push a `vMAJOR.MINOR.PATCH`
tag at that tested commit to promote the exact files to a stable release,
without rebuilding. Repository visibility applies to all package assets.
Package metadata versions are preserved; these are GitHub distribution snapshots,
not automatic PyPI publication or service deployment.

Promotion requires the original Actions artifact (90-day requested retention;
organization policy may shorten it). Expired evidence fails closed: validate a
new main revision. The publisher verifies the run, source, workflow and artifact
digest independently of release metadata. Repository immutable releases must be
enabled. See the [shared release contract](https://github.com/hyperme-sh/.github/blob/3352fb1347e7920ec1d5cd14792ba3038a81abcb/actions/release-channel/README.md).
