from django.contrib import admin

# Register your models here.

from api.models import Article

class ArticleAdmin(admin.ModelAdmin):
	list_display = ('title', 'url', 'created_date')
	list_filter = ['created_date']

admin.site.register(Article, ArticleAdmin)



	# title = models.CharField(max_length=250)
	# url = models.CharField(max_length=250, unique=True)
	# body = models.TextField()
	# article_summary = models.TextField(default="")
	# list_of_keywords = models.TextField(default="")
	# created_date = models.DateTimeField(default=timezone.now)