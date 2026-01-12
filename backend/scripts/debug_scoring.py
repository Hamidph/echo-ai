import re
import unittest

class ScoringDebug(unittest.TestCase):
    def setUp(self):
        # The logic from AnalysisBuilder._compute_visibility
        self._word_boundary_pattern = r"\b{}\b"
    
    def check_visibility(self, brand, response):
        escaped_brand = re.escape(brand)
        prefix = r"\b" if re.match(r"^\w", brand) else ""
        suffix = r"\b" if re.match(r".*\w$", brand) else ""
        
        pattern = re.compile(
            f"{prefix}{escaped_brand}{suffix}",
            re.IGNORECASE,
        )
        matches = list(pattern.finditer(response))
        return len(matches) > 0

    def test_std_case(self):
        # Standard case should pass
        self.assertTrue(self.check_visibility("Starbucks", "I recommend Starbucks."))

    def test_bold_markdown(self):
        # Markdown bold often trips up boundary checks if not careful, 
        # though \b treats * as non-word char, so matches should occur at end of s and start of *
        # \b matches between \w and \W. 's' is \w, '*' is \W. So yes.
        self.assertTrue(self.check_visibility("Starbucks", "Try **Starbucks** coffee."))

    def test_multi_word(self):
        # Space is \W. "Echo AI".
        # \bEcho\ AI\b
        # "Echo AI is good" -> \bEcho matches (start of string), AI\b matches (I followed by space)
        self.assertTrue(self.check_visibility("Echo AI", "Echo AI is great."))

    def test_multi_word_bold(self):
        self.assertTrue(self.check_visibility("Echo AI", "**Echo AI** is usually best."))

    def test_punctuation_in_brand(self):
        # This is where it gets tricky. "Yahoo!"
        # re.escape("Yahoo!") -> "Yahoo\!"
        # \bYahoo\!\b
        # Response: "Yahoo! is cool."
        # \bYahoo match at start. 
        # ! is \W. \b matches between o and !? NO. \b matches between o (\w) and ! (\W).
        # So \bYahoo matches.
        # \! matches !
        # \b matches between ! (\W) and space (\W)? NO. \b is between \w and \W only.
        # So \b at the end of "!" might FAIL if the next char is space.
        # Let's see.
        self.assertTrue(self.check_visibility("Yahoo!", "Yahoo! is cool."))

    def test_apostrophe_brand(self):
        # "McDonald's"
        # re.escape("McDonald's") -> "McDonald's" (apostrophe safe?) or "McDonald\'s"
        # \bMcDonald\'s\b
        # "Go to McDonald's."
        # s is \w. . is \W. Boundary at end works.
        self.assertTrue(self.check_visibility("McDonald's", "Go to McDonald's."))

if __name__ == '__main__':
    unittest.main()
