import unittest

from salary_lookup import (
    format_entry,
    normalize,
    anglicize,
    extract_core_words,
    match_score,
    search_company,
)


class FormatEntryTests(unittest.TestCase):
    def test_zero_count_is_displayed_as_zero(self):
        entry = {
            "company": "Example Corp",
            "city": "",
            "categories": {
                "public_data": {
                    "count": 0,
                    "index": 100.0,
                },
            },
        }

        rendered = format_entry(entry, {"index_baseline": 100, "index_label": "Index"})

        self.assertRegex(rendered, r"Public Data\s+0\s+100\.0")

    def test_text_index_does_not_crash(self):
        entry = {
            "company": "Example Corp",
            "city": "",
            "categories": {
                "sample": {
                    "count": 3,
                    "index": "private",
                },
            },
        }

        rendered = format_entry(entry, {"index_baseline": 100, "index_label": "Index"})

        self.assertIn("private", rendered)

    def test_format_entry_with_zero_baseline(self):
        entry = {
            "company": "Example Corp",
            "city": "",
            "categories": {
                "it": {
                    "count": None,
                    "index": 45000.0,
                },
            },
        }
        rendered = format_entry(entry, {"index_baseline": 0, "index_label": "Salary"})
        self.assertIn("45000.0", rendered)
        self.assertNotIn("%", rendered)

    def test_format_entry_with_custom_baseline(self):
        entry = {
            "company": "Example Corp",
            "city": "",
            "categories": {
                "it": {
                    "count": None,
                    "index": 45000.0,
                },
            },
        }
        rendered = format_entry(entry, {"index_baseline": 40000, "index_label": "Salary"})
        self.assertIn("45000.0", rendered)
        self.assertIn("+12.5%", rendered)


class SearchCompanyTests(unittest.TestCase):
    def test_search_company_with_none_city(self):
        data = {
            "companies": [
                {
                    "company": "Acme",
                    "city": None,
                }
            ]
        }
        results = search_company(data, "Acme", city="Aarhus")
        self.assertEqual(results, [])


class UtilityTests(unittest.TestCase):
    def test_normalize_strips_suffix_and_noise(self):
        self.assertEqual(normalize("Novo Nordisk A/S"), "novonordisk")
        self.assertEqual(normalize("Ørsted (VG) Holding"), "ørsted")
        self.assertEqual(normalize("Chr. Hansen, Denmark Division"), "chrhansen")
        self.assertEqual(normalize("Simple Corp ApS"), "simplecorp")

    def test_anglicize_replaces_danish_chars(self):
        self.assertEqual(anglicize("ørsted"), "orsted")
        self.assertEqual(anglicize("mærsk"), "maersk")
        self.assertEqual(anglicize("ålborg"), "aalborg")

    def test_extract_core_words(self):
        self.assertEqual(extract_core_words("Novo Nordisk A/S"), ["novo", "nordisk"])
        self.assertEqual(extract_core_words("A/S"), [])
        self.assertEqual(extract_core_words("Test Company (Sub-entity)"), ["test", "company"])


class MatchScoreTests(unittest.TestCase):
    def test_exact_match_score(self):
        self.assertEqual(match_score("Novo Nordisk", "Novo Nordisk"), 100)
        self.assertEqual(match_score("novo nordisk", "Novo Nordisk A/S"), 100)

    def test_partial_match_score(self):
        self.assertGreater(match_score("Novo", "Novo Nordisk A/S"), 80)
        self.assertEqual(match_score("Novo Nordisk", "Novo"), 75)

    def test_anglicized_match_score(self):
        self.assertEqual(match_score("Orsted", "Ørsted A/S"), 85)

    def test_overlap_match_score(self):
        # Overlap of multiple words
        self.assertGreater(match_score("Novo Tech", "Novo Nordisk Tech A/S"), 30)

    def test_no_match_score(self):
        self.assertEqual(match_score("Google", "Microsoft"), 0)


class SearchCompanyTests(unittest.TestCase):
    def setUp(self):
        self.data = {
            "companies": [
                {"company": "Novo Nordisk A/S", "city": "Bagsværd"},
                {"company": "Ørsted", "city": "Fredericia"},
                {"company": "Vestas Wind Systems", "city": "Aarhus"},
            ]
        }

    def test_search_by_name(self):
        results = search_company(self.data, "Novo")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["company"], "Novo Nordisk A/S")

    def test_search_with_city_filter(self):
        results = search_company(self.data, "Ørsted", city="Fredericia")
        self.assertEqual(len(results), 1)

        # Mismatching city
        results_wrong_city = search_company(self.data, "Ørsted", city="Bagsværd")
        self.assertEqual(len(results_wrong_city), 0)


if __name__ == "__main__":
    unittest.main()
