"""Run with:  python -m unittest discover tests -v   (no internet / API key needed)"""
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from email_engine import (build_prompt, validate_input, generate_email,
                          clean_output, GenAIError, TONES, LENGTHS)

DEMO = "Offline Demo (no API key)"

CASES = [  # (test no., input, expected subject keyword)
    (1, "I cannot attend college tomorrow because I have a medical appointment.", "Leave"),
    (2, "I cannot attend today's team meeting because of an exam.", "Meeting"),
    (3, "I want to ask HR about the status of my internship application.", "Application"),
    (4, "I need an extension for my assignment submission deadline.", "Extension"),
    (5, "I want to thank my professor for the guidance and support.", "Thank"),
]


class TestValidation(unittest.TestCase):
    def test_empty(self):
        self.assertFalse(validate_input("   ")[0])

    def test_too_short(self):
        self.assertFalse(validate_input("hi")[0])

    def test_too_long(self):
        self.assertFalse(validate_input("a" * 2000)[0])

    def test_valid(self):
        self.assertTrue(validate_input("I am sick today and cannot attend.")[0])


class TestPrompt(unittest.TestCase):
    def test_prompt_contains_parameters(self):
        p = build_prompt("I am sick today", "Formal", "Short", "Asha", "Prof. Rao")
        for s in ("I am sick today", "Formal", "Short", "Asha", "Prof. Rao",
                  "<situation>", "Do not invent"):
            self.assertIn(s, p)


class TestGeneration(unittest.TestCase):
    def test_five_cases_have_full_structure(self):
        for no, text, kw in CASES:
            out = generate_email(text, "Professional", "Medium", DEMO)
            with self.subTest(test=no):
                self.assertTrue(out.startswith("Subject:"))
                self.assertIn(kw, out.split("\n")[0])
                self.assertIn("Dear", out)
                self.assertIn("[Your Name]", out)

    def test_all_tone_length_combinations(self):
        for t in TONES:
            for l in LENGTHS:
                out = generate_email("I cannot attend tomorrow's meeting.", t, l, DEMO, sender_name="Ravi")
                self.assertIn("Ravi", out)

    def test_length_changes_output(self):
        s = generate_email("I am sick today and cannot attend.", "Formal", "Short", DEMO)
        d = generate_email("I am sick today and cannot attend.", "Formal", "Detailed", DEMO)
        self.assertGreater(len(d), len(s))

    def test_missing_key_gives_friendly_error(self):
        os.environ.pop("GEMINI_API_KEY", None)
        with self.assertRaises(GenAIError):
            generate_email("I am sick today and cannot attend.", "Formal", "Short", "Google Gemini")

    def test_invalid_input_rejected(self):
        with self.assertRaises(GenAIError):
            generate_email("", "Formal", "Short", DEMO)


class TestCleanOutput(unittest.TestCase):
    def test_strips_preamble_and_fences(self):
        raw = "Sure! Here you go:\n```\nSubject: Hello\n\nDear **Sir**,\n```"
        out = clean_output(raw)
        self.assertTrue(out.startswith("Subject: Hello"))
        self.assertNotIn("**", out)
        self.assertNotIn("```", out)


if __name__ == "__main__":
    unittest.main()
