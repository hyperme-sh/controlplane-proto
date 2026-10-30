# controlplane-proto

Independent Python distribution for the retained `panopticon.v1` ContractEcho
protocol and generated modules. Generated Python, typing stub and protocol bytes
remain unchanged from source `2d92d13f38d491c298631b9b9296979c1fbadd19`.

Run `bash scripts/check.sh` for locked source checks and fresh-environment wheel
checks. The wheel provides `contractecho_pb2`, `contractecho_pb2_grpc` and the
original protocol source. No monorepo filesystem search is required by consumers.
This is a private package preparation; no tag, public package or runtime cutover
is published. Original source history is retained in `EXTRACTION.json`.

## Isolated component CI

Checks run on disposable GitHub-hosted Ubuntu workers for PRs, main and manual
runs. This repository has no access to the organization self-hosted runner groups,
so PR changes cannot select the shared private fleet. The contents token is
read-only; checkout credentials are not persisted, and no environment/deployment
secrets are provided. The external action allowlist contains only the two full-SHA checkout/uv setup
actions. GitHub also permits local and organization-owned actions. No VM, runner or App is created.

This is the user-authorized isolation correction for new component repositories.
Existing private deployment and payment jobs retain their runner access. An
isolated package check does not authorize publication or runtime cutover.
