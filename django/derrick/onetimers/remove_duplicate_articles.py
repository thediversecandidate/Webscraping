from api.models import Article

all_articles = Article.objects.all()
print("articles count : {}".format(all_articles.count()))

seen = set()
duplicates = 0

for article in all_articles:
    if article.title not in seen:
        seen.add(article)
    else:
        duplicates += 1
        try:
            article.delete()
        except:
            print("Could not delete article : {}".format(article.title))

print("{} duplicates removed".format(duplicates))
