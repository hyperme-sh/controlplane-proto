# controlplane-proto

Independent Python distribution for the retained `panopticon.v1` ContractEcho
protocol and generated modules. Generated Python, typing stub and protocol bytes
remain unchanged from source `2d92d13f38d491c298631b9b9296979c1fbadd19`.

Run `bash scripts/check.sh` for locked source checks and fresh-environment wheel
checks. The wheel provides `contractecho_pb2`, `contractecho_pb2_grpc` and the
original protocol source. No monorepo filesystem search is required by consumers.
This is a private package preparation; no tag, public package or runtime cutover
is published. Original source history is retained in `EXTRACTION.json`.

## Automated execution hold

Repository Actions are disabled. The staged workflow accepts only the main ref
on push/manual dispatch; it does not execute unmerged PR code on the shared
self-hosted runner pool. Before enabling it, verify reviewed/default-branch write
controls and the destination's execution isolation. Automated PR checks need an
isolated runner path; a same-repository condition and read-only workflow token
do not sandbox collaborator-controlled code. Until then, use the local frozen
wheel command above and require review before merge. No runner is provisioned.

The current repository action policy also refuses third-party actions. The staged
main workflow therefore remains inactive pending an explicit least-privilege
action policy and isolated execution review; this work does not broaden that
policy. Local wheel checks do not depend on GitHub action availability.
