# exec(open("custom_scripts/add_word_freq_to_all_models.py").read())

from api.models import Article
from utilities.word_frequency import WordFrequency

wf = WordFrequency()

success, total = 0, 0

all_article_objects = Article.objects.all()

for article_object in all_article_objects:
	# try:
	article_body = article_object.body

	total += 1

	if article_body is not None:
		response_dict = wf.get_frequent_words(article_body)
		
		if response_dict is not None:	
			words = response_dict.get("words", None)
			frequency = response_dict.get("frequency", None)

			article_object.wordcloud_words = " ".join(words)
			article_object.wordcloud_scores = " ".join(list(map(str, frequency)))
			article_object.save()
			success += 1

	# except:
	# 	pass

	
	print("success = {} | fail = {}".format(success, total - success))



