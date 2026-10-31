"""Local behavior checks: no listening sockets, Docker daemon, or external API."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from app import response_for


class ServiceBehaviorTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.data_dir = Path(self.directory.name)

    def run_tool(self, *arguments, stdin=None, check=True):
        return subprocess.run(
            [sys.executable, str(Path(__file__).with_name("data_tool.py")), *arguments],
            input=stdin, capture_output=True, text=True, check=check,
            env={**os.environ, "DATA_DIR": str(self.data_dir)},
        )

    def test_maintenance_affects_readiness_but_not_liveness(self):
        self.assertEqual(response_for("/readyz", self.data_dir)[0], 200)
        self.run_tool("maintenance-on")
        self.assertEqual(response_for("/readyz", self.data_dir)[0], 503)
        self.assertEqual(response_for("/healthz", self.data_dir)[0], 200)
        self.run_tool("maintenance-off")
        self.assertEqual(response_for("/readyz", self.data_dir)[0], 200)

    def test_missing_storage_is_not_ready(self):
        self.assertEqual(response_for("/readyz", self.data_dir / "missing")[0], 503)

    def test_restored_note_matches_original(self):
        self.run_tool("seed", "--text", "Synthetic example 🌱")
        backup = self.run_tool("backup").stdout
        self.run_tool("seed", "--text", "Changed value")
        self.run_tool("restore", stdin=backup)
        self.assertEqual(response_for("/note", self.data_dir),
                         (200, {"note": "Synthetic example 🌱"}))

    def test_invalid_restore_preserves_existing_note(self):
        self.run_tool("seed", "--text", "Keep me")
        result = self.run_tool("restore", stdin=json.dumps({"format": 1, "note": []}), check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(response_for("/note", self.data_dir)[1]["note"], "Keep me")

    def test_oversized_note_is_rejected(self):
        result = self.run_tool("seed", "--text", "x" * 4097, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.data_dir / "note.txt").exists())

    def test_unknown_routes_are_not_successful(self):
        self.assertEqual(response_for("/not-a-route", self.data_dir)[0], 404)


if __name__ == "__main__":
    unittest.main()
