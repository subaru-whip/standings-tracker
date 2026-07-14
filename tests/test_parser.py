import datetime
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parser import parse_filename
from roster import load_roster

ROSTER_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "roster.json")


class TestParser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.roster = load_roster(ROSTER_PATH)
        cls.fallback_mtime = datetime.datetime(2026, 7, 12, 19, 55, 59).timestamp()

    def parse(self, filename, mtime=None):
        return parse_filename(filename, self.roster, mtime or self.fallback_mtime)

    def test_clean_dash_format(self):
        p = self.parse("7.13 - Harry - Skatepark IMG_0001.jpg")
        self.assertEqual(p.person, "Harry")
        self.assertEqual(p.department, "Skatepark")
        self.assertEqual(p.date, "7/13")
        self.assertTrue(p.date_from_filename)

    def test_no_space_dash_format(self):
        p = self.parse("7.13-Laina-RPG 20260713_094953.jpg")
        self.assertEqual(p.person, "Laina")
        self.assertEqual(p.department, "RPG")
        self.assertEqual(p.date, "7/13")

    def test_no_dash_space_format(self):
        p = self.parse("7.13 Seleia Art IMG_3014.jpeg")
        self.assertEqual(p.person, "Seleia")
        self.assertEqual(p.department, "Art")
        self.assertEqual(p.date, "7/13")

    def test_laina_stapleton_alias_no_date_no_dept(self):
        p = self.parse("Laina Stapleton 20260713_101250.jpg")
        self.assertEqual(p.person, "Laina")
        self.assertEqual(p.department, "Unknown")
        self.assertFalse(p.date_from_filename)
        self.assertEqual(p.date, "7/12")  # from fallback mtime

    def test_sophieobe_alias_concatenated(self):
        p = self.parse("SophieObe IMG_4010.jpeg")
        self.assertEqual(p.person, "Sophie")
        self.assertEqual(p.department, "Unknown")
        self.assertFalse(p.date_from_filename)

    def test_kc_alias_no_space_dash_format(self):
        p = self.parse("7.13-KC-Aeroial IMG_6157.jpeg")
        self.assertEqual(p.person, "Kristi")
        self.assertEqual(p.department, "Aeroial")
        self.assertEqual(p.date, "7/13")

    def test_william_macom_alias_no_date_no_dept(self):
        p = self.parse("William Macom IMG_2204.jpeg")
        self.assertEqual(p.person, "Bill")
        self.assertEqual(p.department, "Unknown")
        self.assertFalse(p.date_from_filename)

    def test_lowercase_name_matches_canonical_casing(self):
        p = self.parse("7.13 - glenn - Sound City IMG_5217.jpeg")
        self.assertEqual(p.person, "Glenn")
        self.assertEqual(p.department, "Sound City")

    def test_maddy_and_maddie_stay_distinct(self):
        p1 = self.parse("7.13 - Maddy - Bunk IMG_0001.jpg")
        p2 = self.parse("7.13 - Maddie - Bunk IMG_0002.jpg")
        self.assertEqual(p1.person, "Maddy")
        self.assertEqual(p2.person, "Maddie")
        self.assertNotEqual(p1.person, p2.person)

    def test_dedup_key_same_for_dup_suffix_with_space(self):
        p1 = self.parse("7.13 - glenn - Sound City IMG_5218.jpeg")
        p2 = self.parse("7.13 - glenn - Sound City IMG_5218 (1).jpeg")
        self.assertEqual(p1.dedup_key, p2.dedup_key)

    def test_dedup_key_same_for_dup_suffix_without_space(self):
        p1 = self.parse("Laina Stapleton 20260713_101250.jpg")
        p2 = self.parse("Laina Stapleton 20260713_101250(0).jpg")
        self.assertEqual(p1.dedup_key, p2.dedup_key)

    def test_dedup_key_differs_for_different_photos(self):
        p1 = self.parse("7.13 - glenn - Sound City IMG_5217.jpeg")
        p2 = self.parse("7.13 - glenn - Sound City IMG_5218.jpeg")
        self.assertNotEqual(p1.dedup_key, p2.dedup_key)

    def test_lolo_alias_broken_separator_routes_to_laura(self):
        p = self.parse(
            "LOLO - 07[]12 - Airport pictures "
            "15CC6387-BCEF-4686-A0DC-B2654EEEBC2B_1_105_c.jpeg"
        )
        self.assertEqual(p.person, "Laura")
        self.assertIsNone(p.unmatched_guess)
        self.assertEqual(p.department, "Airport pictures")
        self.assertEqual(p.date, "7/12")
        self.assertTrue(p.date_from_filename)


if __name__ == "__main__":
    unittest.main()
