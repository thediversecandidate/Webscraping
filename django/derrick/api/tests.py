from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from api.models import Article
from utilities.word_frequency import WordFrequency


class WordFrequencyTests(SimpleTestCase):
    """Tests for the WordFrequency utility."""

    def test_get_frequent_words(self):
        """get_frequent_words should return the most common words."""
        text = "This is a test. This test is simple. Words words words."
        wf = WordFrequency()
        result = wf.get_frequent_words(text, number_of_stopwords=5)

        self.assertEqual(result["words"], ["words", "test", "simple"])
        self.assertEqual(result["frequency"], [3, 2, 1])


class AuthenticatedAPITestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="pw")
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)


class ArticlesByPageTests(AuthenticatedAPITestCase):
    def test_requires_authentication(self):
        anon_client = APIClient()
        resp = anon_client.get("/articles/page/1/")
        self.assertEqual(resp.status_code, 401)

    def test_returns_404_when_page_has_no_articles(self):
        resp = self.client.get("/articles/page/1/")
        self.assertEqual(resp.status_code, 404)

    def test_returns_partial_last_page_instead_of_404(self):
        # Regression test: a page whose end index is past the last
        # article, but whose start index is still in range, should return
        # the available articles rather than 404.
        # bulk_create (not create) so this doesn't trigger the
        # django-elasticsearch-dsl post_save signal, which would otherwise
        # require a live Elasticsearch connection just to seed test data.
        Article.objects.bulk_create([
            Article(title="Article %d" % i, url="https://example.com/%d" % i, body="body")
            for i in range(15)
        ])

        resp = self.client.get("/articles/page/2/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 5)


class ArticlesByKeywordTests(AuthenticatedAPITestCase):
    def test_filters_by_keyword_case_insensitively(self):
        # bulk_create to avoid needing a live Elasticsearch connection --
        # see the comment in ArticlesByPageTests above.
        Article.objects.bulk_create([
            Article(title="Hyperscale Data Centers", url="https://example.com/1", body="body"),
            Article(title="Something else entirely", url="https://example.com/2", body="body"),
        ])

        resp = self.client.get("/articles/keyword/hyperscale")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]["title"], "Hyperscale Data Centers")


class SearchArticlesByKeywordTests(AuthenticatedAPITestCase):
    def test_returns_500_instead_of_crashing_when_search_backend_fails(self):
        # Regression test: search_articles_by_keyword used to reference
        # `serializer` outside the try block, so an exception during the
        # Elasticsearch query raised an unrelated UnboundLocalError instead
        # of a clean error response.
        with patch("api.views.ArticleDocument.search", side_effect=Exception("es down")):
            resp = self.client.get("/articles/search/test/0/5/desc")

        self.assertEqual(resp.status_code, 500)
