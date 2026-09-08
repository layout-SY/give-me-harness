from __future__ import annotations

import hashlib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ArchiveIntegrityTests(unittest.TestCase):
    def test_remaining_v1_history_matches_its_sha256_manifest(self) -> None:
        archive = ROOT / "archive/v1-admin-ui-pre-core"
        entries = []
        for line in (archive / "MANIFEST.sha256").read_text(encoding="utf-8").splitlines():
            expected, relative = line.split("  ", 1)
            entries.append((expected, relative.removeprefix("./")))

        self.assertGreater(len(entries), 100)
        for expected, relative in entries:
            with self.subTest(relative=relative):
                source = archive / relative
                self.assertTrue(source.is_file())
                self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), expected)

    def test_retired_automatic_distribution_archive_is_absent(self) -> None:
        archive_directories = tuple(sorted(
            path.name for path in (ROOT / "archive").iterdir() if path.is_dir()
        ))

        self.assertEqual(
            archive_directories,
            ("consumer-policy-retirement-2026-09-08", "v1-admin-ui-pre-core"),
        )


if __name__ == "__main__":
    unittest.main()
