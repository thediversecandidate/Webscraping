from django.contrib import admin

# Register your models here.

from api.models import Article

class ArticleAdmin(admin.ModelAdmin):
	pass

admin.site.register(Article, ArticleAdmin)
