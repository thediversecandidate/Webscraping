from django.contrib import admin

# Register your models here.

from api.models import Article

class ArticleAdmin(admin.ModelAdmin):
	list_display = ('title', 'url', 'created_date', 'published_date')
	list_filter = ['created_date']

admin.site.register(Article, ArticleAdmin)
