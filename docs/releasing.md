# Releasing controlplane-proto

Channel rules for tags, Actions artifacts, and the JSON records under
`releases/`. The [README](../README.md) keeps the short version. Compatibility
rules for a candidate bundle are in [release-policy.md](release-policy.md) and
in the [Spanopticon release policy](https://github.com/hyperme-sh/spanopticon/blob/main/docs/releases.md).

## Versions you will see

Several numbers are in use at once. They name different things.

| Where | Value | What it is |
| --- | --- | --- |
| `pyproject.toml` | `0.2.0` | Version of a wheel built from this tree. Distribution name `controlplane-proto`, wheel filename `controlplane_proto-0.2.0-py3-none-any.whl`. |
| `release-policy.json` `line`, and `release-line` in the admission workflows | `0.2` | Line passed into Spanopticon component admission for this repository. |
| GitHub release `v0.24.0` | package `0.24.0` | Immutable stable release. Assets include `controlplane_proto-0.24.0-py3-none-any.whl`, `controlplane_proto-0.24.0.tar.gz`, and `release-manifest.json`. Recorded under `releases/accepted/`. |
| `.github/test-channel.json` `next` | `0.24.0` | Test-bundle train. Tags look like `0.24.0-test.N`. The current bundle `0.24.0-test.0` carries the `0.2.0` wheel built from main. |

A test-bundle tag uses the channel version. The wheel inside keeps the version
from `pyproject.toml` at the commit that was built. Publishing a test bundle
leaves the accepted stable record and the dependency pins unchanged.

## Main qualification artifacts

`.github/workflows/check.yml` (Component checks) runs `bash scripts/check.sh`
on pull requests, on pushes to `main`, and on manual runs. On a push to `main`
it uploads the wheel and sdist from that run as the Actions artifact
`tested-dist` (90-day retention, uncompressed). It also uploads
`protocol-test-results`. Those artifacts are the bytes later publication jobs
ship. Component checks itself stops at the artifact upload.

## Contract snapshots

`scripts/export_release_contract.py` writes two files for one wheel:

- `contract.json` — schema version, the protobuf file descriptor as JSON, and
  the SHA-256 of each packaged runtime and resource file
  (`contractecho_pb2.py`, `contractecho_pb2.pyi`, `contractecho_pb2_grpc.py`,
  `controlplane_proto_data/contractecho.proto`).
- `evidence.json` — distribution name, package version, wheel SHA-256, wheel
  size, and the SHA-256 of `contract.json`.

The exporter hashes the wheel bytes, then reads the generated `DESCRIPTOR`
assignment as a Python literal. It rejects a wheel with duplicate entries, the
wrong distribution name or version, or any runtime file outside that set.
A formatting change in the generated modules or the packaged `.proto` changes
the contract. A version-only metadata edit leaves `contract.json` unchanged.

`scripts/check.sh` exports the contract for the wheel it just built and for the
wheel rebuilt from the sdist, and requires the two `contract.json` files to be
byte-identical. The fresh install of each wheel must match every captured file
digest and the descriptor taken from that wheel. When
`releases/qualification/current/release.json` or
`releases/candidate/release.json` is present, the same script checks that
manifest against the export.

`evidence.json` records artifact inspection of that wheel. It has no acceptance
flag and no publication URL. Publisher provenance, equivalence of the generated
code to a separate protocol source, consumer compatibility, and an accepted
release baseline are separate steps.

## Test snapshots and `test-<commit>` prereleases

GitHub prereleases tagged `test-<full-commit-sha>` are development snapshots.
The package version embedded in the wheel is the version of that build.
Artifact and consumer evidence for those snapshots lives under
`releases/qualification/`. `releases/qualification/current/` is the current
wheel binding and is marked `stable_release: false`. Older receipts live under
`releases/qualification/snapshots/<commit>/` with a `classification.json` of
kind `qualified-test-snapshot`.

Stable acceptance is `releases/accepted/` for an immutable `v*` release, named
by the repository variable `SPANOPTICON_RELEASE_BASELINE_SHA`. Test snapshots
stay under `releases/qualification/`.

## Stable releases

A stable publication is a non-draft, non-prerelease GitHub release tagged
`vMAJOR.MINOR.PATCH`. Pushing that tag runs `.github/workflows/release.yml`:

1. Release admission calls the pinned Spanopticon workflow
   `hyperme-sh/spanopticon/.github/workflows/component-release.yml` with
   `release-line` `0.2`, `baseline-ref` set to
   `SPANOPTICON_RELEASE_BASELINE_SHA`, and `requested-version` set to the tag.
   The same admission workflow (`.github/workflows/release-admission.yml`) also
   runs on any tag push and on a manual run that passes an exact version.
   Development pull requests use `.github/workflows/version-policy.yml` and the
   package tests.
2. When admission succeeds, the publish job runs the pinned
   `hyperme-sh/.github/actions/release-channel` action with
   `workflow: .github/workflows/check.yml`. The action publishes the `tested-dist`
   artifact from the matching successful main run. It checks the run, the source
   revision, and the artifact digest. That job's only step is the pinned action:
   the workflow has no checkout and no package install. On this public repository
   the job runs on `ubuntu-24.04`.

The publisher repeats those checks against the retained artifact and the
baseline. If `SPANOPTICON_RELEASE_BASELINE_SHA` is unset or names a commit
without the accepted record, admission stops and the publish job stays skipped.

The accepted record in this tree is tag `v0.24.0`:

- `releases/accepted/release.json` — line `0.24`, component version `0.24.0`,
  contract digest, and the wheel's `urn:sha256:` URI.
- `releases/accepted/provenance.json` — repository `hyperme-sh/controlplane-proto`,
  tag `v0.24.0`, source revision, GitHub release id, and the SHA-256 of each
  published asset.
- Release URL: <https://github.com/hyperme-sh/controlplane-proto/releases/tag/v0.24.0>.

That record is the component baseline for this package. Runtime deployment and
downstream consumer acceptance stay separate from it. A later stable tag still
has to match the declared contract and the exact main artifact.
Replacing the bytes of an already published version is rejected. A candidate
submitted for that check belongs at `releases/candidate/release.json` and has
to name this component, use the configured line, and match `pyproject.toml`.

## Coordinated test bundles

`.github/test-channel.json` opts this repository into the `next: 0.24.0` train
and names `.github/workflows/check.yml` as the qualifying workflow.

`.github/workflows/test-bundles.yml` runs when Component checks completes on
`main`. It publishes only when that run succeeded and was a push. The job calls
the pinned `hyperme-sh/.github/actions/bundle-channel` action with `mode: test`.
The action checks the workflow run, the source revision, the channel
configuration, and the original `tested-dist` digest, and uploads those bytes
as an immutable prerelease `0.24.0-test.N`. It reads the retained artifact and
the channel configuration. Bundles are published from successful main pushes.

`0.24.0-test.0` is the bundle published from that channel. Its assets are the
`0.2.0` wheel and sdist plus `release-manifest.json`. Later `N` values are the
channel's own counter. A consumer pins the component commit and the artifact
digest. The counter belongs to the channel.

A missing `tested-dist` artifact, or a tag that already exists, stops the job
before it publishes. Promoting a test bundle to the stable `v*` release is a
separate tag publication through the stable workflow above.
