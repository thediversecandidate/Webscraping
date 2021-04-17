from api.serializers import ArticleSerializer
from api.models import Article
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes

from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from api.documents import ArticleDocument

from django.conf import settings


@api_view(('GET',))
def index(request):
    return Response('Hello world!')

@api_view(('GET',))
def test_endpoint(request):
    
    ans = "Failed"

    try:
        v = settings.SMMRY_API_ENDPOINT
        ans = str(v)
    except Exception as e:
        raise e

    return Response(ans)


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


@api_view(('GET',))
@permission_classes([IsAuthenticated])
def search_articles_by_keyword(request, keyword, first, no_of_results, sort_by):

    try:
        keyword = (str(keyword)).strip()

        sort_by_field = "created_date"

        if sort_by == "desc":
            sort_by_field = '-created_date'

        queryset = ArticleDocument.search().query("match", body=keyword).sort(sort_by_field)[int(first):int(no_of_results)]

        serializer = ArticleSerializer(queryset, many=True)

    except Exception as e:
        print(e)

    return Response(serializer.data)


@api_view(('GET',))
@permission_classes([IsAuthenticated])
def get_total_results_by_keyword(request, keyword):
    keyword = (str(keyword)).strip()

    count = 0
    try:
        queryset = ArticleDocument.search().query("match", body=keyword)
        count = queryset.count()

    except Exception as e:
        print(e)

    return Response({'count' : count})
