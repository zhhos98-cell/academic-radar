import py_compile
import unittest
from pathlib import Path


class GuiPackagingTests(unittest.TestCase):
    def test_gui_sources_compile(self):
        root = Path(__file__).resolve().parents[1]
        py_compile.compile(str(root / "academic_radar" / "gui.py"), doraise=True)
        py_compile.compile(str(root / "academic_radar_gui.py"), doraise=True)

    def test_default_bluesky_queries_are_line_based(self):
        gui_path = Path(__file__).resolve().parents[1] / "academic_radar" / "gui.py"
        source = gui_path.read_text(encoding="utf-8")
        self.assertIn('DEFAULT_BSKY_QUERIES =', source)
        self.assertIn('"call for papers" "history of science"', source)
        self.assertIn('"fellowship" "history of science"', source)


if __name__ == "__main__":
    unittest.main()
