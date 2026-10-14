"""Check HA add-on metadata and image ownership before tagging a release."""

import re
import sys
import tomllib
from pathlib import Path

from ruamel.yaml import YAML

root = Path(__file__).resolve().parents[1]
yaml = YAML(typ="safe")
config = yaml.load((root / "config.yaml").read_text())
project = tomllib.loads((root / "pyproject.toml").read_text())["project"]
version = re.search(r'__version__ = "([^"]+)"', (root / "src/mylo/__init__.py").read_text())[1]
assert config["version"] == project["version"] == version
if len(sys.argv) > 1:
    assert sys.argv[1] == version, "tag differs from manifest version"
assert config["slug"] == "mylo_siliconflow"
assert config["arch"] == ["amd64", "aarch64"]
assert config["image"] == "ghcr.io/letsgodancing/{arch}-addon-mylo-siliconflow"
assert config["url"] == "https://github.com/Letsgodancing/mylo-siliconflow"
assert yaml.load((root.parent / "repository.yaml").read_text())["url"] == config["url"]
assert "siliconflow" in config["schema"]["llm_provider"]
assert config["options"]["siliconflow_url"] == "https://api.siliconflow.cn/v1"
for file in ("Dockerfile", "build.yaml", "rootfs/etc/services.d/mylo/run", "LICENSE", "NOTICE"):
    assert (root / file).is_file(), file
workflow = (root.parent / ".github/workflows/release.yml").read_text()
assert "oasis-enterprise/" not in workflow
assert "letsgodancing/${{ matrix.arch }}-addon-mylo-siliconflow" in workflow
print(f"HA repository metadata and image ownership verified: {version}")
