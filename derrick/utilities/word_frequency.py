
# import necessary modules
from wordcloud import STOPWORDS as wordcloud_stopwords
from collections import Counter
import time

# for regular expressions checking
import re

# separate module for getting stop words
# good design in case this needs to be changes
def get_stop_words():
	return wordcloud_stopwords


class WordFrequency():

	# initialize and instance and load stop_words into memory for faster access
	def __init__(self):
		self.stopwords = get_stop_words()


	def get_frequent_words(self, body_of_text, number_of_stopwords=25):
		
		# get all the words that are "words" using regex
		regex_input_text = re.split(r"\W+", body_of_text)

		# empty list declared
		cleaned_words = []

		# iterating through all words
		for index, word in enumerate(regex_input_text):
			# if a valid word, and size is greater than 2
			if (word not in self.stopwords) and (len(word) > 2):
				cleaned_words.append(word)

		# create word frequency map using Collections
		word_freq_map = Counter(cleaned_words)

		# get the top N words, default to 25
		top_n_words = word_freq_map.most_common(number_of_stopwords)

		words = []
		frequency = []

		# create separate lists
		for W, F in top_n_words:
			words.append(W)
			frequency.append(F)

		final_word_cloud =  { "words" : words, "frequency" : frequency }

		# return the response
		return final_word_cloud

		
