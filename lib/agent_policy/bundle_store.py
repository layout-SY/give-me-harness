"""기존 경로를 유지하는 검증된 정책 원본 보존과 누락 복구."""

from __future__ import annotations

import json
import os
import re
import shutil
import tempfile
from pathlib import Path

from .core import PolicyError, atomic_write, sha256_bytes
from .injection import BUNDLE_MANIFEST, bundle_diagnostics
from .runtime import load_runtime


def backup_directory(assignment_path: Path, record: dict) -> Path:
    if (re.fullmatch(r"[a-f0-9]{64}", str(record.get("bundle_digest", ""))) is None
            or not Path(record.get("bundle_root", "")).is_absolute()):
        raise PolicyError("bundle 백업의 원래 경로 또는 digest가 올바르지 않습니다.")
    return (assignment_path.parents[4] / "bundle-backups" / record["bundle_digest"] /
            sha256_bytes(record["bundle_root"].encode()))


def copy_manifest_files(source: Path, destination: Path) -> None:
    manifest = json.loads((source / BUNDLE_MANIFEST).read_bytes())
    for relative in [*manifest["files"], BUNDLE_MANIFEST]:
        if Path(relative).is_absolute() or ".." in Path(relative).parts:
            raise PolicyError("원본 보존 manifest 경로가 올바르지 않습니다.")
        target = source / relative
        if target.is_symlink() or not target.resolve().is_relative_to(source.resolve()):
            raise PolicyError("원본 보존 파일이 symlink이거나 bundle 밖에 있습니다.")
        atomic_write(destination / relative, target.read_bytes())


def preserve_bundle(assignment_path: Path, record: dict) -> Path:
    state = load_runtime("runtime_state")
    with state.locked(assignment_path.parents[2] / "events.lock"):
        record = state.read(assignment_path)
        source = Path(record["bundle_root"])
        if not bundle_diagnostics(source, record["bundle_digest"])["valid"]:
            raise PolicyError("검증된 원본 bundle만 보존할 수 있습니다.")
        destination = backup_directory(assignment_path, record)
        manifest_hash = sha256_bytes((source / BUNDLE_MANIFEST).read_bytes())
        if destination.exists():
            if (not bundle_diagnostics(destination, record["bundle_digest"])["valid"] or
                    sha256_bytes((destination / BUNDLE_MANIFEST).read_bytes()) != manifest_hash):
                raise PolicyError("기존 bundle 백업이 원본과 다릅니다. 덮어쓰지 않습니다.")
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            temporary = Path(tempfile.mkdtemp(prefix=".preserve-", dir=destination.parent))
            try:
                copy_manifest_files(source, temporary)
                if (not bundle_diagnostics(temporary, record["bundle_digest"])["valid"] or
                        sha256_bytes((temporary / BUNDLE_MANIFEST).read_bytes()) != manifest_hash):
                    raise PolicyError("보존 중 원본이 변경되었습니다.")
                os.rename(temporary, destination)
            finally:
                if temporary.exists():
                    shutil.rmtree(temporary)
        record["bundle_backup_manifest_sha256"] = manifest_hash
        state.write(assignment_path, record)
        return destination


def restore_bundle(assignment_path: Path, record: dict) -> Path:
    source = backup_directory(assignment_path, record)
    target = Path(record["bundle_root"])
    manifest_hash = record.get("bundle_backup_manifest_sha256")
    if (not manifest_hash or not bundle_diagnostics(source, record["bundle_digest"])["valid"] or
            sha256_bytes((source / BUNDLE_MANIFEST).read_bytes()) != manifest_hash):
        raise PolicyError("검증 가능한 원본 bundle 백업이 없습니다. 대화 기록을 열람하거나 새 정책으로 인계하세요.")
    if not target.is_absolute() or target.resolve() != target or target.exists() or target.is_symlink():
        raise PolicyError("누락된 원래 bundle의 정확한 경로에만 복구할 수 있습니다.")
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=".restore-", dir=target.parent))
    try:
        copy_manifest_files(source, temporary)
        if not bundle_diagnostics(temporary, record["bundle_digest"])["valid"]:
            raise PolicyError("복구된 원본 bundle 검증에 실패했습니다.")
        if target.exists() or target.is_symlink():
            raise PolicyError("복구 중 대상 경로가 생겼습니다. 다시 확인하세요.")
        os.rename(temporary, target)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
    return target
