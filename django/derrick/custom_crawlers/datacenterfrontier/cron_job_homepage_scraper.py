import time
import requests
import bs4
from collections import OrderedDict as OD
import dateutil.parser as dparser

from api.models import Article

from django.conf import settings

def get_summary_and_keywords_from_smmry_api(article_url):

    print("Waiting for 5 seconds before calling SMMRY api.")
#     time.sleep(5)

    try:

        params = OD()

        API_ENDPOINT = settings.SMMRY_API_ENDPOINT
        params['SM_API_KEY'] = settings.SM_API_KEY
        params['SM_LENGTH'] = settings.SMMRY_API_ENDPOINT
        params['SM_KEYWORD_COUNT'] = settings.SM_KEYWORD_COUNT
        params['SM_URL'] = article_url

        r = requests.get(API_ENDPOINT, params=params)

        data = r.json()

        list_of_keywords = data.get('sm_api_keyword_array', [])
        article_summary = data.get('sm_api_content', "Error")

        response = {
            'list_of_keywords' : list_of_keywords,
            'article_summary' : article_summary
        }

        return response

    except Exception as e:
        print("Some exception occurred")
        return ({})

def get_article_content_from_url(article_url):

    print("waiting for 30 Seconds before starting WebPage Scraper")
    print(article_url)
    time.sleep(30)
    try:

        # body
        r = requests.get(article_url)
        soup = bs4.BeautifulSoup(r.text)

        body = soup.find('div', {'class': 'entry-content'})

        paras = []

        for i, c in enumerate(body.contents):
            try:
                all_paras = c.findAll('p')
                for p in all_paras:
                    paras.append(p.text)
            except:
                pass

        article_body = '\n\n'.join(paras)

        published_date = ""
    
        try:
            published_date = soup.find('time', {'class' : 'entry-time'}).text
            published_date = dparser.parse(published_date, fuzzy=True)
        except:
            pass

        response = {
            'body' : article_body,
            'published_date' : published_date
        }
        
        print(published_date)
        return response

    except:

        print("Some Error occurred while Parsing Webpage")
        return




def extract_links_from_homepage():
    
    base_url = "https://datacenterfrontier.com"

    r = requests.get(base_url)

    soup = bs4.BeautifulSoup(r.text)
    titles = soup.findAll('header', {'class' : 'entry-header'})

    data = []

    for title in titles:
        try:
            anchor = title.find('a')
            title = anchor.text.strip()
            url = anchor['href']
            item = {'title' : title, 'url' : url}
            data.append(item)
            
        except:
            print("Some exception occurred")

    return data


def add_record_to_db(title, url, body, published_date, article_summary, list_of_keywords):
    # import pdb; pdb.set_trace()
    try:
        print("Saving New Article to DB")
        new_article = Article(title=title, 
                                url=url, 
                                body=body,
                                published_date=published_date,
                                article_summary=article_summary, 
                                list_of_keywords=list_of_keywords
                                )
        new_article.save()
    except:
        print("Failed to save Article to DB. Probably ElasticSearch BuildIndex error")


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

    print("="*50)
	print("Total items : {}".format(len(items)))
	print("="*50)

    for item in items:
        article_title = item['title']
        article_url = item['url']

        if not article_url_exists_in_db(article_url):
            # scrape and parse the article body from URL
            article_content = get_article_content_from_url(article_url)
            
            if not article_content:
                print("Could not extract article content")
                return
            
            data_from_smmry_api = get_summary_and_keywords_from_smmry_api(article_url)

            # Get Article Summary from SMMRY API
            article_summary = data_from_smmry_api.get('article_summary', "")
            
            # Get Keywords from SMMRY API
            list_of_keywords = ""

            _keywords = data_from_smmry_api.get('list_of_keywords', [])
            if len(_keywords) > 0:
                list_of_keywords = " ".join([word.lower() for word in _keywords])
        
            # Create Model and Save it to DB
            add_record_to_db(url=article_url, 
                            title=article_title, 
                            body=article_content['body'],
                            published_date=article_content['published_date'],
                            article_summary=article_summary, 
                            list_of_keywords=list_of_keywords
                            )
        else:
			print("URL : {} already exists in DB".format(article_url))