# Release compatibility

`release-policy.json` names this repository, component `controlplane-proto`,
line `0.2`, and the package version file `pyproject.toml` (currently `0.2.0`).
The pinned Spanopticon workflow checks that configuration on pull requests.
Version changes or a `releases/candidate/release.json` submission also require
release admission. Every tag push and manual release request requires admission.
A configuration-only check is a configuration result. Release compatibility is
the admission result.

Components that share a release line share major and minor versions. Patch
numbers advance independently and keep their accepted API contracts. Installing
this workflow leaves recorded package versions as they are.

The accepted stable record under `releases/accepted/` is line `0.24`, package
`0.24.0`, tag `v0.24.0`. Tags and that record are documented in
[releasing.md](releasing.md).

Before attempting a release:

1. Produce a real accepted bundle at `releases/accepted/release.json`, with its
   contract files and immutable artifact references. Set the repository variable
   `SPANOPTICON_RELEASE_BASELINE_SHA` to its full 40-character commit SHA. The first
   baseline needs automated artifact/consumer qualification and provenance;
   examples and invented digests are not accepted release evidence.
2. Generate the candidate bundle at `releases/candidate/release.json` from the
   release artifacts. It must contain exactly this component, use the line from
   `release-policy.json` (`0.2`), and match every declared package version and
   the requested tag.
3. Run admission against the trusted baseline. Patch contracts must remain
   unchanged; changing a published artifact at the same version is rejected.
   Verify artifact provenance and downstream consumer behavior separately.
4. Make successful admission and artifact/consumer validation automated
   prerequisites of the publisher for the exact release. Select the accepted
   baseline independently of candidate data and retain the validation evidence.
   Admission compares the candidate with the trusted baseline inside the pipeline.

Missing baselines stop admission. This workflow neither publishes nor deploys and
does not enable repository Actions, grant private dependency access, or prove
that a declared artifact exists. See the [Spanopticon release policy](https://github.com/hyperme-sh/spanopticon/blob/main/docs/releases.md)
for the manifest format and compatibility rules.

## Artifact-backed baseline and candidate

`releases/accepted` records the `0.24.0` protocol wheel for tag `v0.24.0`.
`provenance.json` binds that record to the source revision, the GitHub release
id, and the published asset digests. It is the component baseline for this
package.

A candidate names the built wheel with a content-addressed `urn:sha256:` URI.
Package CI rebuilds the wheel and rejects any mismatch in its version, digest,
or exported contract before retaining publishable bytes. Stable publication
also requires automated release admission. The downloadable release URL is
supplied when that publication runs. Channel behavior for Actions artifacts,
`test-<commit>` snapshots, and the `v0.24.0` release is documented in
[releasing.md](releasing.md). Automatic package prereleases are not published.
