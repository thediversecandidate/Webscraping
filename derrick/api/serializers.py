from rest_framework import serializers
from api.models import Article


class ArticleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Article
        fields = ['id', 'url', 'title', 'body', 'article_summary', 'list_of_keywords', 'wordcloud_words', 'wordcloud_scores', 'created_date']

