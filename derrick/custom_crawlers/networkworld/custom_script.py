
import time
import requests
import bs4

from api.scraper_utils import add_record_to_db
from api.models import Article

def scraper(link):
		
	if not ("/article/" in link):
		print("Invalid Link : {}".format(link))

	try:

		r = requests.get(link)
		soup = bs4.BeautifulSoup(r.text)

		# import pdb; pdb.set_trace()
		
		body = soup.find('div', {'itemprop' : 'articleBody'})
		
		paras = []

		for i, c in enumerate(body.contents):
			if (c.__class__ == bs4.element.Tag):
				if (c.attrs == {}):
					if len(c.text.strip()) > 0:
						paras.append(c.text.strip())
		
		
		article_body = '\n\n'.join(paras)

		headline = soup.find('h1', {'itemprop' : 'headline'})
		if headline is None:
			return None
		else:
			headline = soup.find('h1', {'itemprop' : 'headline'}).text

		summary = soup.find('h3', {'itemprop' : 'description'})
		if summary is None:
			summary = paras[0]
		else:
			summary = soup.find('h3', {'itemprop' : 'description'}).text


		return {'headline' : headline, 'summary' : summary, 'article_body' : article_body}

	except:

		return None


f = open("network_links.txt")
article_urls = f.read().split('\n')

seen = set()
i = 1
for article_url in article_urls:

	print("waiting for 2 secs")
	time.sleep(2)

	print("Processing : {}".format(article_url))

	data = scraper(article_url)

	if data is None:
		continue
		print("Error for link : {}".format(article_url))
		add_record_to_db(url=article_url, title="", body="", article_summary="", list_of_keywords="")

	else:
		# print(data)

		article_title = data["headline"]
		article_body = data["article_body"]
		article_summary = data["summary"]
		list_of_keywords = ""

		try:
			new_article = Article(title=article_title, url=article_url, body=article_body, article_summary=article_summary, list_of_keywords=list_of_keywords)
			new_article.save()

			print("{} Done".format(i))
			i += 1
		
		except:
			pass



