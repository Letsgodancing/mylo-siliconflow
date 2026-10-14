# Releasing Mylo SiliconFlow

Upstream base: Oasis-Enterprise/mylo v1.9.0. Preserve LICENSE and NOTICE.

1. Inside mylo_siliconflow/, update config.yaml, pyproject.toml and src/mylo/__init__.py to the same version.
2. Inside mylo_siliconflow/, update CHANGELOG.md and docs/SILICONFLOW_RELEASE.md; run CI and scripts/validate_release.py.
3. Push a version tag such as v1.9.0.1. The release workflow tests, builds both architectures, pushes GHCR images, verifies anonymous manifest/layer downloads, then creates the GitHub release.
4. On the first publication, GitHub may create each GHCR package as private. Set both packages (amd64-addon-mylo-siliconflow and aarch64-addon-mylo-siliconflow) to public in package settings, then rerun the publish job. A public repository alone does not guarantee public packages. Release publication deliberately fails until anonymous pulls succeed.

The add-on image template is ghcr.io/letsgodancing/{arch}-addon-mylo-siliconflow. HA Supervisor selects the architecture and uses config.yaml's version as the image tag. Never point the manifest at the upstream owner's images.

For upstream updates, fetch the upstream remote, review the latest non-prerelease tag, merge it into a maintenance branch, retain SiliconFlow and isolation changes, update all versions and release notes, then run CI before tagging. No unattended merge of upstream code is enabled.
