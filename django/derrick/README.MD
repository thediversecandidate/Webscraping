# Django Application that works as API and runs a CRON Job

How to run :

```
python manage.py runserver 0.0.0.0:80
```

## Admin Page

```
https://api.thediversecandidate.com/admin
username : derrick
password : derrick
```

## View Analytics Dashboard

```
https://api.thediversecandidate.com/analytics/
```

## Add this to the Request Headers when calling the GET Request.

- You can find this token and create new ones from the Django Admin Dashboard. You can test it using Postman by adding the following key-value pair in Postman

```
Key : "Authorization"
Value : "Token fd314d4436dfdc9fd990822cd1e483d951c7dfd6"
```

## Get Articles by Page number

```
# Example
https://api.thediversecandidate.com/articles/page/1
```

## Get Article by Searching for a keyword

```
# Template
https://api.thediversecandidate.com/articles/keyword/<keyword>/<max_number_of_results>

# Example
https://api.thediversecandidate.com/articles/keyword/Google/25
```

## Get Total number of results present in DB for a given Keyword

```
# Template
https://api.thediversecandidate.com/articles/results/<keyword>

# Example
https://api.thediversecandidate.com/articles/results/Xeon
```

# How to Crawl a New Site

- Make a copy of any existing folder in the directory `custom_crawlers`
- Rename the folder to the site you want to scrape, for example : `datacenterknowledge.com`
- Make necessary changes in the functionsin the `crawl_for_links.py` file. The changes should be minimal, depending on the structure of the new website.
- Once, you've made the changes, run the script using the command `python crawl_for_links.py` and the script should start crawling and a new file named `article_links.txt` will be populated with links as the cralwers runs.
- Next, make necessary changes in the `scrape_article_page()` function in the file `scrape_article_body_and_save_to_db.py`.
- cd to the home directory of the app and run the Django Shell using the command `./manage.py shell`.
- Finally, we need to run the script which will scrape the contents of the links containing an article and will add the data to the DB. Type the following command within the Django shell to start running the script : `exec(open("custom_crawlers/<site_name>/scrape_article_body_and_save_to_db.py").read())`. Don't forget to replace `<site_name>` with the folder you created in the first step, for example : `networkworld`.
- You should be able to see the progress of the Script as it runs.

# Word-Cloud Module

- The `WordFreqency.py` is added to generate a `word:freqency` pair that can be generated from a given input. This module will be used by the Frontend to generate a Word-Cloud and display it on the frontend.
- Dependencies :
  - `nltk` for word tokenization
  - `Counter` from the Collections to easily generate frequency map
  - `re` for regular-expression matching

### Usage

- To use the module in your app, import module using `from utilities.word_frequency import WordFrequency`
- Create Instance, for example `wf = WordFrequency()`
- Use the `get_frequent_words()` method and pass a body of text as input
- Output will be a Python Dictionary Object with keys `words` and `frequency`

## Changelog :

- 28/06/2020
  - Added `created_data` as a parameter to be return on all queries
  - added `django-silk` for Profiling all requests handled by the server
  - added `word_frequency` module in the `utilities` directory to generate a `word:freq` map from a given body of text.
