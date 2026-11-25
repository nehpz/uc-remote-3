# SPDX-License-Identifier: MPL-2.0

import hashlib
import io
import json
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path

from tools.validate_archive import validate_archive


class ArchivePreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "fixture.tar.gz"
        self.metadata = {"driver_id": "example-fixture", "version": "0.1.0-rc.1", "name": {"en": "Fixture"}}
        self.js = ("bin/driver.js", b"console.log('fixture');", 0o644)

    def write_archive(self, *files, link=None):
        with tarfile.open(self.path, "w:gz") as archive:
            entries = [("driver.json", json.dumps(self.metadata).encode(), 0o644), *files]
            for name, data, mode in entries:
                member = tarfile.TarInfo(name)
                member.size = len(data)
                member.mode = mode
                archive.addfile(member, io.BytesIO(data))
            if link:
                member = tarfile.TarInfo(link)
                member.type = tarfile.SYMTYPE
                member.linkname = "bin/driver.js"
                archive.addfile(member)

    def test_accepts_node_layout_and_returns_digest(self):
        self.write_archive(self.js, ("./config/example.json", b"{}", 0o644))
        self.assertEqual(
            validate_archive(self.path),
            ("example-fixture", hashlib.sha256(self.path.read_bytes()).hexdigest()),
        )

    def test_cli_passes_valid_layout_and_reports_no_runtime_verification(self):
        self.write_archive(("bin/driver", b"not executed", 0o755))
        result = subprocess.run(
            [sys.executable, "tools/validate_archive.py", str(self.path)],
            capture_output=True, text=True, check=True,
        )
        self.assertIn("runtime and device compatibility not verified", result.stdout)

    def test_cli_rejects_unreadable_archive(self):
        self.path.write_bytes(b"not an archive")
        result = subprocess.run(
            [sys.executable, "tools/validate_archive.py", str(self.path)],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("Archive preflight failed", result.stderr)

    def test_rejects_reserved_id(self):
        self.metadata["driver_id"] = "uc_fixture"
        self.write_archive(self.js)
        with self.assertRaisesRegex(ValueError, "reserved"):
            validate_archive(self.path)

    def test_rejects_malformed_release_version(self):
        self.metadata["version"] = "0.1.0-01"
        self.write_archive(self.js)
        with self.assertRaisesRegex(ValueError, "Semantic Versioning"):
            validate_archive(self.path)

    def test_rejects_missing_or_ambiguous_entry_point(self):
        for files in [(), (self.js, ("bin/driver", b"not executed", 0o755))]:
            with self.subTest(files=files):
                self.write_archive(*files)
                with self.assertRaisesRegex(ValueError, "exactly one"):
                    validate_archive(self.path)

    def test_rejects_unsafe_or_unknown_paths(self):
        for path in ("bin/../secret", "/config/secret", "misc/settings.json"):
            with self.subTest(path=path):
                self.write_archive(self.js, (path, b"{}", 0o644))
                with self.assertRaisesRegex(ValueError, "path is not portable|unexpected archive root"):
                    validate_archive(self.path)

    def test_rejects_links(self):
        self.write_archive(self.js, link="config/link")
        with self.assertRaisesRegex(ValueError, "unsupported archive entry"):
            validate_archive(self.path)

    def test_rejects_normalized_duplicate(self):
        self.write_archive(self.js, ("./bin/driver.js", b"duplicate", 0o644))
        with self.assertRaisesRegex(ValueError, "duplicate path"):
            validate_archive(self.path)

    def test_rejects_executable_config(self):
        self.write_archive(self.js, ("config/install", b"not executed", 0o755))
        with self.assertRaisesRegex(ValueError, "executable file outside bin"):
            validate_archive(self.path)

    def test_rejects_non_directory_parent(self):
        self.write_archive(self.js, ("bin/deps", b"file", 0o644), ("bin/deps/entry", b"file", 0o644))
        with self.assertRaisesRegex(ValueError, "non-directory parent"):
            validate_archive(self.path)

    def test_accepts_declared_root_icon_but_rejects_missing_one(self):
        self.metadata["icon"] = "custom:test.png"
        self.write_archive(self.js, ("test.png", b"not inspected", 0o644))
        validate_archive(self.path)
        self.write_archive(self.js)
        with self.assertRaisesRegex(ValueError, "declared custom icon"):
            validate_archive(self.path)
