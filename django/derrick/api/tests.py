from django.test import SimpleTestCase

from utilities.word_frequency import WordFrequency


class WordFrequencyTests(SimpleTestCase):
    """Tests for the WordFrequency utility."""

    def test_get_frequent_words(self):
        """get_frequent_words should return the most common words."""
        text = "This is a test. This test is simple. Words words words."
        wf = WordFrequency()
        result = wf.get_frequent_words(text, number_of_stopwords=5)

        self.assertEqual(result["words"], ["words", "test", "simple"])
        self.assertEqual(result["frequency"], [3, 2, 1])
