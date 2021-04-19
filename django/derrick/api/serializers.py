from rest_framework import serializers
from api.models import Article


class ArticleSerializer(serializers.ModelSerializer):
	created_date = serializers.SerializerMethodField()
	published_date = serializers.SerializerMethodField()

	class Meta:
		model = Article
		fields = ['id', 'url', 'title', 'body', 'article_summary', 'list_of_keywords', 'wordcloud_words', 'wordcloud_scores', 'created_date', 'published_date']

	def get_created_date(self, obj):
		return str(obj.created_date)[:10]

	def get_published_date(self, obj):
		return str(obj.published_date)[:10]		