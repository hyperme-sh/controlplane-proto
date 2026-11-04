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
