import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import spintax_check as sc  # noqa: E402


class SpintaxTest(unittest.TestCase):
    def test_valid_copy(self):
        text = "{Hi|Hey|Hello} {{first_name}},\n\n{Quick question|One question}: {is|would} this useful?"
        errors, warnings, nodes = sc.check(text)
        self.assertEqual(errors, [])
        self.assertEqual(sc.count_versions(nodes), 3 * 2 * 2)
        out = sc.render(nodes, random.Random(0), {"first_name": "Anna"})
        self.assertIn("Anna", out)
        self.assertNotIn("{", out)

    def test_nested_spins_count(self):
        _, _, nodes = sc.check("{a|{b|c} d}")
        self.assertEqual(sc.count_versions(nodes), 3)

    def test_unclosed_and_stray(self):
        self.assertTrue(sc.check("{Hi|Hey there")[0])
        self.assertTrue(sc.check("Hi} there")[0])
        self.assertTrue(sc.check("Hi | there")[0])
        self.assertTrue(sc.check("{{first_name}")[0])

    def test_empty_option(self):
        errors, _, _ = sc.check("{Hi||Hey}")
        self.assertTrue(any("empty" in e for e in errors))

    def test_single_brace_variable(self):
        errors, _, _ = sc.check("Hi {first_name},")
        self.assertTrue(any("double braces" in e for e in errors))

    def test_variable_inside_spin_warns(self):
        _, warnings, _ = sc.check("{Hi {{first_name}}|Hey}")
        self.assertTrue(any("inside a spin" in w for w in warnings))

    def test_spam_words_en_and_sv(self):
        _, warnings, _ = sc.check("Get it free! Klicka här. Guaranteed!!")
        joined = " ".join(warnings)
        self.assertIn('"free"', joined)
        self.assertIn('"klicka här"', joined)
        self.assertIn('"guaranteed"', joined)
        self.assertIn("exclamation", joined)

    def test_spam_word_boundaries(self):
        _, warnings, _ = sc.check("We are carefree and freely available.")
        self.assertFalse(any('"free"' in w for w in warnings))

    def test_links_flagged(self):
        _, warnings, _ = sc.check("See https://example.com")
        self.assertTrue(any("link" in w for w in warnings))

    def test_main_exit_codes(self):
        import io
        import contextlib
        import tempfile
        good = Path(tempfile.mkdtemp()) / "good.txt"
        good.write_text("{Hi|Hey} {{first_name}}")
        bad = good.with_name("bad.txt")
        bad.write_text("{Hi|Hey {{first_name}}")
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(sc.main([str(good)]), 0)
            self.assertEqual(sc.main([str(bad)]), 1)


if __name__ == "__main__":
    unittest.main()
