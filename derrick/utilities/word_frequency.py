from wordcloud import STOPWORDS as wordcloud_stopwords
from collections import Counter
import time
import re

def get_stop_words():
	return wordcloud_stopwords


class WordFrequency():

	def __init__(self):
		self.stopwords = get_stop_words()

	def get_frequent_words(self, body_of_text, number_of_stopwords=25):
		regex_input_text = re.split(r"\W+", body_of_text)

		cleaned_words = []

		for index, word in enumerate(regex_input_text):
			if (word not in self.stopwords) and (len(word) > 2):
				cleaned_words.append(word)

		word_freq_map = Counter(cleaned_words)

		top_n_words = word_freq_map.most_common(number_of_stopwords)

		words = []
		frequency = []

		for W, F in top_n_words:
			words.append(W)
			frequency.append(F)

		final_word_cloud =  { "words" : words, "frequency" : frequency }

		return final_word_cloud

		
