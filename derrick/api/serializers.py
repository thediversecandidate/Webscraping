from rest_framework import serializers
from api.models import Article


class ArticleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Article
        fields = ['id', 'url', 'title', 'body']