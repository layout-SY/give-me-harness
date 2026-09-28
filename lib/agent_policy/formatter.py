"""워크트리와 독립된 고정 버전 Prettier 설치. 소비자 의존성은 설치하지 않는다."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from .core import CENTRAL_ROOT, PolicyError, read_json
from .runtime import load_runtime


def install() -> Path:
    source = CENTRAL_ROOT / "policy/common/contracts"
    package = read_json(source / "prettier-package.json")
    version = package["dependencies"]["prettier"]
    if read_json(source / "runtime-policy.json")["formatting"]["version"] != version:
        raise PolicyError("Prettier 설치 manifest와 runtime 버전이 다릅니다.")
    target = CENTRAL_ROOT / "state/tools/prettier" / version
    state = load_runtime("runtime_state")
    with state.locked(target.parent / "install.lock"):
        if target.exists():
            if target.is_symlink() or read_json(target / "node_modules/prettier/package.json").get("version") != version:
                raise PolicyError(f"공용 Prettier 설치가 손상되었습니다: {target}")
            return target
        npm = shutil.which("npm")
        if not npm:
            raise PolicyError("공용 Prettier 설치에 npm이 필요합니다.")
        with tempfile.TemporaryDirectory(prefix=".install-", dir=target.parent) as temporary:
            staging = Path(temporary) / "package"
            staging.mkdir()
            shutil.copyfile(source / "prettier-package.json", staging / "package.json")
            shutil.copyfile(source / "prettier-package-lock.json", staging / "package-lock.json")
            result = subprocess.run([npm, "ci", "--ignore-scripts", "--no-audit", "--no-fund",
                "--cache", str(CENTRAL_ROOT / "state/npm-cache")], cwd=staging, text=True, capture_output=True)
            if result.returncode:
                raise PolicyError(f"공용 Prettier 설치 실패: {result.stderr.strip()}")
            os.replace(staging, target)
    return target
