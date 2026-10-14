"""Verify anonymous GHCR manifest AND layer access (no GitHub credentials)."""

import json
import sys
from urllib.request import Request, urlopen

version = sys.argv[1]
accept = ", ".join([
    "application/vnd.oci.image.index.v1+json",
    "application/vnd.oci.image.manifest.v1+json",
    "application/vnd.docker.distribution.manifest.list.v2+json",
    "application/vnd.docker.distribution.manifest.v2+json",
])
for arch, platform in [("amd64", "amd64"), ("aarch64", "arm64")]:
    name = f"letsgodancing/{arch}-addon-mylo-siliconflow"
    with urlopen(f"https://ghcr.io/token?service=ghcr.io&scope=repository:{name}:pull", timeout=60) as response:
        token = json.load(response)["token"]
    headers = {"Authorization": f"Bearer {token}", "Accept": accept}

    def fetch(path):
        with urlopen(Request(f"https://ghcr.io/v2/{name}/{path}", headers=headers), timeout=60) as response:
            return json.load(response)

    manifest = fetch(f"manifests/{version}")
    if "manifests" in manifest:
        descriptor = next(m for m in manifest["manifests"] if m.get("platform", {}).get("architecture") == platform)
        manifest = fetch(f"manifests/{descriptor['digest']}")
    config = fetch(f"blobs/{manifest['config']['digest']}")
    assert config["architecture"] == platform, config["architecture"]
    assert config["config"]["Labels"]["org.opencontainers.image.version"] == version
    assert config["config"]["Labels"]["org.opencontainers.image.source"] == "https://github.com/Letsgodancing/mylo-siliconflow"
    for layer in manifest["layers"]:
        with urlopen(Request(f"https://ghcr.io/v2/{name}/blobs/{layer['digest']}", headers=headers), timeout=60) as response:
            assert response.read(1), "empty layer"
    print(f"Public manifest, correct architecture and anonymous layer downloads verified: {name}:{version}")
