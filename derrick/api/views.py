from django.contrib.auth.models import User, Group
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from rest_framework import permissions
from api.serializers import ArticleSerializer
from api.models import Article
from django.http import JsonResponse
from django.http import HttpResponse
from rest_framework.decorators import api_view, renderer_classes, permission_classes
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

@api_view(('GET',))
def index(request):
    return Response('Hello world!')

@api_view(('GET',))
@permission_classes([IsAuthenticated])
def get_articles_by_page(request, page_num):

    page_num = int(page_num)
    start = (page_num - 1) * 10
    end = page_num * 10

    number_of_articles = Article.objects.count()

    if end > number_of_articles:
        return HttpResponse(status=404)

    articles = Article.objects.all()[start:end]
    serializer = ArticleSerializer(articles, many=True)
    return Response(serializer.data)

@api_view(('GET',))
@permission_classes([IsAuthenticated])
def get_articles_by_keyword(request, keyword):

    keyword = str(keyword)

    response = []

    queryset = Article.objects.all()
    for q in queryset:
        if keyword in q.title:
            response.append(q)

    print(len(response))
    serializer = ArticleSerializer(response, many=True)
    return Response(serializer.data)

