"""Offline smoke tests: no ISO download or Wii files are used."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
SOURCE = HERE / "tools" / "vita" / "psd09_wizard.py"
SPEC = importlib.util.spec_from_file_location("psd09_wizard", SOURCE)
wizard = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(wizard)


def disc_header(game_id=b"RMCE01", nkit=False, correct_magic=True):
    data = bytearray(0x204)
    data[:6] = game_id
    if correct_magic:
        data[0x18:0x1C] = bytes.fromhex("5d1c9ea3")
    if nkit:
        data[0x200:0x204] = b"NKIT"
    return bytes(data)


class HeaderTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)

    def make(self, name, data):
        path = self.root / name
        path.write_bytes(data)
        return path

    def test_clean_usa_iso(self):
        self.assertEqual(wizard.inspect_disc(self.make("mkw.iso", disc_header())), "RMCE01")

    def test_clean_usa_wbfs(self):
        prefix = bytearray(512)
        prefix[:4] = b"WBFS"
        prefix[8] = 9
        prefix[12] = 1
        self.assertEqual(
            wizard.inspect_disc(self.make("mkw.wbfs", prefix + disc_header())),
            "RMCE01",
        )

    def test_wrong_region(self):
        with self.assertRaisesRegex(wizard.ConversionError, "RMCE01"):
            wizard.inspect_disc(self.make("eu.iso", disc_header(game_id=b"RMCP01")))

    def test_nkit(self):
        with self.assertRaisesRegex(wizard.ConversionError, "NKit"):
            wizard.inspect_disc(self.make("mkw.iso", disc_header(nkit=True)))

    def test_invalid_iso(self):
        with self.assertRaisesRegex(wizard.ConversionError, "valida"):
            wizard.inspect_disc(self.make("bad.iso", disc_header(correct_magic=False)))

    def test_rvz_disallowed(self):
        with self.assertRaisesRegex(wizard.ConversionError, "ISO o WBFS"):
            wizard.inspect_disc(self.make("mkw.rvz", disc_header()))

    def test_missing_disc(self):
        with self.assertRaisesRegex(wizard.ConversionError, "no existe"):
            wizard.inspect_disc(self.root / "missing.iso")


if __name__ == "__main__":
    unittest.main()
