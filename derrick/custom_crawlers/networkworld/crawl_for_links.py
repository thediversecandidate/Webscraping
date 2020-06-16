import requests
from bs4 import BeautifulSoup
from collections import deque
import time
import logging
logging.basicConfig(filename='networkworld_articles.log', level=logging.INFO)

class Scraper:
    
    def __init__(self):
        self.base_url = "https://www.networkworld.com"
        self.visited_links = set()
        self.article_urls = set()
        self.queue = deque()
        self.start_time = time.time()
        
    def initialize(self):
        self.queue.append(self.base_url)
        
    def start(self):
        
        # Initialize start time
        self.start_time = time.time()
        
        while self.queue:
            
            url = self.queue.popleft()
            print(url)
#             import pdb; pdb.set_trace()
            
            if url in self.visited_links:
                continue
                
            self.visited_links.add(url)
            
            if self.page_is_article(url):
                self.article_urls.add(url)
                self.append_to_file(url)
                print("PAGE : {} contains an article. \nTotal found till now : {}".format(url, len(self.article_urls)))
                # TODO parse article page
                
            page_source = self.get_page_source(url)
            
            if page_source is not None:
                    
                new_links = self.extract_relevant_links(page_source)
                
                if new_links is not None:
                    for link in new_links:
                        if link not in self.visited_links:
                            self.queue.append(link)
        
        self.scraping_complete()

    def append_to_file(self, data):
        f = open(os.path.join(os.getcwd(), "article_links.txt"), "a+")
        f.write(data + "\n")
        f.close()
        
    def page_is_article(self, url):

        try:

            split_url = url.split('/')
            
            if (len(split_url) >= 6) and (split_url[3] == "article"):
                return True

        except:
            print("\nException occured in page_is_article()")
            return False
    
    def extract_relevant_links(self, page_source):
        
        try:
        
            soup = BeautifulSoup(page_source)
            all_links = soup.findAll('a')

            relevant_links = []

            for i, l in enumerate(all_links):
                if l.has_key('href'):
                    if l['href'].startswith('/'):
                        if not (self.base_url in l):
                            relevant_links.append(self.base_url + l['href'])

#             for i, link in enumerate(relevant_links):
#                 print(i, link)
#             import pdb; pdb.set_trace()
            return relevant_links
        
        except:
            print("\nException occured in extract_relevant_links()")
            return False
            
    
    def get_page_source(self, url):
        
        try:
            r = requests.get(url)
            return r.text
        except:
            print("Could not get page source for {}".format(url))
            return None
        
    
    def scraping_complete(self):
        # TODO
        end_time = time.time()
        print("Scraping Complete.")
        print("Article URLs found : {}".format(len(self.article_urls)))
        print("Total Time : {} secs".format(end_time - self.start_time))

if __name__ == "__main__":

    scraper = Scraper()
    scraper.initialize()
    scraper.start()

        
