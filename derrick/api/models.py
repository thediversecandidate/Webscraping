from django.db import models
from django.utils import timezone

# Create your models here.

class Article(models.Model):
	title = models.CharField(max_length=250)
	url = models.CharField(max_length=250, unique=True)
	body = models.TextField()
	article_summary = models.TextField(default="")
	list_of_keywords = models.TextField(default="")
	created_date = models.DateTimeField(default=timezone.now)

	def __str__(self):
		return self.title

	class Meta:
		ordering = ['title']

	class Admin:
		pass

