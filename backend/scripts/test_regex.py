import re

def test_visibility_regex():
    brand = "Starbucks"
    # The actual pattern used in AnalysisBuilder
    # self._word_boundary_pattern = r"\b{}\b"
    pattern = re.compile(rf"\b{re.escape(brand)}\b", re.IGNORECASE)

    test_cases = [
        ("I love Starbucks coffee.", True),
        ("starbucks is great.", True),
        ("Starbucks's coffee is okay.", False), # Possessive might fail with \b on right side? Actually ' is a word boundary in Python re? Let's see.
        ("Go to Starbucks!", True),
        ("The Starbucks.", True),
        ("Anti-Starbucks sentiment.", True),
        ("Starbucks?", True),
        ("Starbuckscoffee", False), # Should be False
        ("TheStarbucks", False),    # Should be False
        ("Star barks", False),      # Should be False
        ("At Starbucks, we...", True)
    ]

    print(f"Testing regex pattern: {pattern.pattern} for brand '{brand}'\n")

    all_passed = True
    for text, expected in test_cases:
        match = bool(pattern.search(text))
        result = "PASS" if match == expected else "FAIL"
        if match != expected:
            all_passed = False
        print(f"[{result}] Text: '{text}' -> Match: {match} (Expected: {expected})")

    if all_passed:
        print("\nAll baseline tests passed.")
    else:
        print("\nSome tests failed.")

if __name__ == "__main__":
    test_visibility_regex()
