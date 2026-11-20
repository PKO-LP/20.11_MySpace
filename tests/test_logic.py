import sys
import math
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from storage import load_notes, save_notes
from motion import orbit_position, next_angle, zoom_distance
from planet_data import PLANETS, FACTS


class LogicTests(unittest.TestCase):
    def test_orbit_radius(self):
        for angle in range(0, 720, 13):
            x, y, z = orbit_position(8, angle)
            self.assertAlmostEqual(math.hypot(x, z), 8)

    def test_pause(self):
        self.assertEqual(next_angle(42, 25, .1, 10, True), 42)

    def test_frame_independence(self):
        a = next_angle(0, 25, 1, 1, False)
        b = 0
        for _ in range(100):
            b = next_angle(b, 25, .01, 1, False)
        self.assertAlmostEqual(a, b)

    def test_speed(self):
        self.assertEqual(next_angle(0, 25, 1, 5, False), 125)

    def test_zoom_limits(self):
        self.assertEqual(zoom_distance(2, 1, 3, 65), 3)
        self.assertEqual(zoom_distance(65, -1, 3, 65), 65)

    def test_notes_roundtrip_and_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / 'data' / 'notes.txt'
            self.assertEqual(load_notes(p), {})
            save_notes(p, {'earth': 'Моя Земля | океаны', 'mars': 'Красный'})
            self.assertEqual(load_notes(p)['earth'], 'Моя Земля | океаны')
            save_notes(p, {'earth': 'Новая\nстрока'})
            self.assertEqual(load_notes(p), {'earth': 'Новая строка'})
            self.assertFalse(p.with_suffix('.tmp').exists())

    def test_bad_lines(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / 'notes.txt'
            p.write_text('мусор\n|без ключа\nearth|Земля', encoding='utf-8')
            self.assertEqual(load_notes(p), {'earth': 'Земля'})

    def test_data(self):
        self.assertEqual(len(PLANETS), 8)
        self.assertEqual(len(FACTS), 8)
        self.assertEqual(len({p[0] for p in PLANETS}), 8)
        self.assertEqual([p[2] for p in PLANETS], sorted(p[2] for p in PLANETS))

    def test_save_failure_is_reported(self):
        with tempfile.TemporaryDirectory() as folder:
            parent = Path(folder) / 'file'
            parent.write_text('not a directory')
            with self.assertRaises(OSError):
                save_notes(parent / 'notes.txt', {'earth': 'text'})


if __name__ == '__main__':
    unittest.main()
