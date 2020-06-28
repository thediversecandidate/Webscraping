# exec(open("custom_scripts/add_word_freq_to_all_models.py").read())

# import Article Model
from api.models import Article

# import the word_frequency module from utilities folder
from utilities.word_frequency import WordFrequency

# create Instance
wf = WordFrequency()

success, total = 0, 0

# get queryset of all Articles
all_article_objects = Article.objects.all()

for article_object in all_article_objects:
	try:
		# get article body
		article_body = article_object.body

		total += 1

		# check if article_body response failed or not 
		if article_body is not None:

			# get words:freq from the body of the article
			response_dict = wf.get_frequent_words(article_body)
			
			if response_dict is not None:	
				words = response_dict.get("words", None)
				frequency = response_dict.get("frequency", None)

				# add words as a list
				article_object.wordcloud_words = " ".join(words)
				
				# add frequencies as a list of strings
				article_object.wordcloud_scores = " ".join(list(map(str, frequency)))
				
				# update and save the Article Object
				article_object.save()
				
				success += 1

	except:
		pass

# for logging	
print("success = {} | fail = {}".format(success, total - success))



