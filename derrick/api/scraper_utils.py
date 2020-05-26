import time
import requests
from bs4 import BeautifulSoup as bs4


def scraper_datacenter():
	print("Parsing has begun")
	start_time = time.time()
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
			print("Some exception occured")

	end_time = time.time()
	print("Time taken : {} seconds".format(end_time - start_time))
	return data


	