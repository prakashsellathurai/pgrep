from .regex import match_pattern
import unittest

class TestStringMethods(unittest.TestCase):
    def test_basic_literal(self):
        assert match_pattern("abc", "abc")
        assert not match_pattern("abcd", "abc$")
        assert match_pattern("abc", "^abc$")
        assert not match_pattern("ab", "abc")

    def test_dot_wildcard(self):
        assert match_pattern("abc", "a.c")
        assert not match_pattern("ac", "a.c")

    def test_quantifiers(self):
        assert match_pattern("aaa", "a+")
        assert match_pattern("", "a*")
        assert match_pattern("a", "a?")
        assert match_pattern("", "a?")

    def test_character_classes(self):
        assert match_pattern("a", "[abc]")
        assert not match_pattern("d", "[abc]")
        assert match_pattern("d", "[^abc]")
        assert not match_pattern("a", "[^abc]")

    def test_escape_digits_and_words(self):
        assert match_pattern("1", r"\d")
        assert not match_pattern("a", r"\d")
        assert match_pattern("a", r"\w")
        assert match_pattern("1", r"\w")
        assert not match_pattern("@", r"\w")

    def test_groups_and_alternations(self):
        assert match_pattern("cat", "(cat|dog)")
        assert match_pattern("dog", "(cat|dog)")
        assert not match_pattern("cow", "(cat|dog)")
        assert match_pattern("a cat", "a (cat|dog)")
        assert match_pattern("dogdogdog", "(dog)+")

    def test_complex_patterns(self):
        pattern = r"^I see (\d (cat|dog|cow)s?(, | and )?)+$"
        text = "I see 1 cat, 2 dogs and 3 cows"
        assert match_pattern(text, pattern)

        text2 = "I see 1 cat 2 dogs 3 cows"
        assert not match_pattern(text2, pattern)

if __name__ == '__main__':
    unittest.main()