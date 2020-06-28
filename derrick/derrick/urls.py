"""derrick URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from api import views


# router = routers.DefaultRouter()
# router.register(r'posts', views.ArticleViewSet, basename='ArticleViewSet')

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.index, name='index'),
    path('articles/page/<page_num>/', views.get_articles_by_page, name='articles-by-page'),
    path('articles/keyword/<keyword>', views.get_articles_by_keyword, name='get_articles_by_keyword'),
    path('articles/search/<keyword>/<no_of_results>', views.search_articles_by_keyword, name='search_articles_by_keyword'),
    path('test/', views.test_endpoint, name='test_endpoint'),

]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
