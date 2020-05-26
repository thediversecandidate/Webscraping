import time
import requests
from bs4 import BeautifulSoup as bs4

from api.models import Article

def get_article_body_from_url(article_url):
	return("This is the body of the article")

def extract_links_from_homepage():
	
	base_url = "https://www.datacenterknowledge.com"

	r = requests.get(base_url)

	soup = bs4(r.text)
	titles = soup.findAll('div', {'class' : 'title'})

	data = []

	for title in titles:
		try:
			anchor = title.find('a')
			title = anchor.text.strip()
			url = base_url + anchor['href']
			item = {'title' : title, 'url' : url}
			data.append(item)
		except:
			print("Some exception occurred")

	return data


def add_record_to_db(title, url, body):
	new_article = Article(title=title, url=url, body=body)
	new_article.save()


def article_url_exists_in_db(url):

	exists = False

	try:
		exists = Article.objects.get(url=url)
	except:
		print("URL {} does not exists in DB".format(url))

	return exists



def scraper_datacenter():
	print("Parsing has begun")

	items = extract_links_from_homepage()

	if len(items) == 0:
		print("No links extracted from homepage.")
		return

	# iterate through all links and check if URL exists in DB
	# If it doesn't, add it to the DB

	for item in items:
		article_title = item['title']
		article_url = item['url']

		if not article_url_exists_in_db(article_url):
			# scrape and parse the article body from URL
			article_body = get_article_body_from_url(article_url)

			# Create Model and Save it to DB
			add_record_to_db(url=article_url, title=article_title, body=article_body)




	

	


	