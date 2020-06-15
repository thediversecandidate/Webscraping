from api.models import Article
from api.scraper_utils import get_summary_and_keywords_from_smmry_api 
import time

articles = Article.objects.all()

for a in articles:
	if a.article_summary == "":
		data_from_smmry_api = get_summary_and_keywords_from_smmry_api(a.url)

		# Get Article Summary from SMMRY API
		article_summary = data_from_smmry_api.get('article_summary', "")
		
		# Get Keywords from SMMRY API
		list_of_keywords = ""

		_keywords = data_from_smmry_api.get('list_of_keywords', [])
		if len(_keywords) > 0:
			list_of_keywords = " ".join([word.lower() for word in _keywords])

		print(a.url)
		print(article_summary)
		print(list_of_keywords)
		print("\n")

		a.article_summary = article_summary
		a.list_of_keywords = list_of_keywords

		a.save()

		print("Sleeping for 10 seconds...")
		print("\n")
		time.sleep(10)
