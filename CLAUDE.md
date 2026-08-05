# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## SECURITY WARNING — read before touching anything

`django/derrick/derrick/settings.py` previously had a hardcoded Django
`SECRET_KEY`, RDS Postgres host/user/`PASSWORD`, and an `SM_API_KEY`
committed in plaintext, and `django/derrick/README.MD` documented a
plaintext admin username/password and a live DRF auth token. **This
repository is public**, so all of those values must be treated as
permanently compromised even now that the code has been fixed — see
"Secrets remediation status" below for exactly what is/isn't done.

Do not add further secrets to tracked files, do not hardcode any new
credential, and always read config from environment variables (see
`django/derrick/.env.example` for the required var names) going forward.

### Secrets remediation status

Code fixed (this repo no longer contains the literal values): `SECRET_KEY`,
`DB_PASSWORD`/`DB_HOST`/`DB_USER`, `SMMRY_API_KEY` now come from environment
variables in `settings.py`, and `README.MD` no longer prints the admin
password or a live token.

**Still needs action outside this repo, by someone with infrastructure
access** (an AI agent working in this checkout cannot do this — it requires
AWS/Django-admin credentials this task was not given):
- Rotate the RDS Postgres password for `derrick.c6takndlw3wu.us-east-1.rds.amazonaws.com`
  and set the new value as `DB_PASSWORD` wherever the app actually runs.
- Change the Django admin password for the `derrick` account.
- Generate a fresh DRF auth token from the admin panel and delete the old
  one (`...7dfd6`, also duplicated in the `ElasticSearchPOC` repo).
- Rotate the SMMRY API key.
- Set `DJANGO_SECRET_KEY` to a new random value in the deployed environment
  (a leaked `SECRET_KEY` can forge session/password-reset tokens).
- These values also still exist in this repo's **git history** even after
  the latest commit removes them from the file contents — scrubbing history
  (`git filter-repo` or a fresh repo) is a separate, deliberate action a
  human should decide on, not something to do silently as a side effect of
  an unrelated change.

## What this is

A Django 3.1 REST API (app name `derrick`, project root
`django/derrick/`) that crawls a fixed set of tech-news sites, stores
scraped articles in Postgres, indexes them into Elasticsearch, and serves
them through a keyword-search API. Originally deployed at
`api.thediversecandidate.com`.

## Running / testing locally

```bash
./setup.sh                                   # venv + pip install -r django/derrick/requirements.txt
cd django/derrick
cp .env.example .env   # fill in DJANGO_SECRET_KEY, DB_*, SMMRY_API_KEY -- see settings.py
python manage.py migrate
python manage.py runserver 0.0.0.0:80
python manage.py test api --verbosity 2      # test suite (api app only)
```

Needs Postgres reachable per `derrick/settings.py` env vars for the tests to
run at all. The full app additionally needs Elasticsearch reachable (search
endpoints and *any* `Article` row save/delete -- see "Elasticsearch is a
hard dependency of plain DB writes" below), and Redis + Celery for the
async task queue (`derrick/celery.py`, `supervisor/derrick_celery.conf`,
`supervisor/derrick_celerybeat.conf`). `rebuild_elastic_index.sh` /
`restart_server.sh` / `status.sh` are the deploy-time operational scripts
(not part of the test loop). Confirmed working (2026-08): a fresh
`pip install -r requirements.txt` + `manage.py test` + `manage.py runserver`
smoke test against a real local Postgres, with `DJANGO_DEBUG=1`.

### Elasticsearch is a hard dependency of plain DB writes

`django_elasticsearch_dsl`'s `post_save`/`post_delete` signal handlers
(registered via `api/documents.py`'s `@registry.register_document`) run
synchronously on every `Article.save()`/`.delete()`, including plain
`Article.objects.create(...)`. If Elasticsearch is unreachable, **any code
that saves an `Article` raises**, not just the search endpoints -- this
includes the crawler scripts. Test code that only needs a DB row (not a
search-indexed one) should use `Article.objects.bulk_create([...])`
instead of `.create()`/`.save()`, since `bulk_create` doesn't fire signals
-- see `api/tests.py` for the pattern. This coupling is a real fragility in
the running app too (a blip in ES availability breaks scraping, not just
search) and would be worth decoupling (e.g. index asynchronously via a
Celery task) if this pipeline is being hardened further.

## Architecture

- `api/` — the Django app: `models.py` (single `Article` model: title, url,
  body, summary, keywords, wordcloud data, dates), `views.py` (function-based
  DRF views, most gated by `IsAuthenticated` + the `TokenAuthentication`
  scheme), `serializers.py`, `documents.py` (django-elasticsearch-dsl
  document mapping for `Article`), `tasks.py` (Celery tasks).
- `custom_crawlers/<site>/` — one directory per scraped site
  (`datacenterknowledge`, `datacenterfrontier`, `networkworld`), each with
  its own `crawl_for_links.py` (site-specific link discovery ->
  `article_links.txt`) and `scrape_article_page()` in
  `scrape_article_body_and_save_to_db.py`. Adding a new site means copying
  an existing folder and adapting these two scripts to that site's HTML
  structure — see the "How to Crawl a New Site" section of
  `django/derrick/README.MD` for the exact manual workflow (crawl script ->
  run it standalone -> paste the scrape function's output into `manage.py
  shell` via `exec(open(...).read())`). This is a manual, per-site process,
  not a generic scraper framework.
- `cron_jobs/` — scheduled scraping entry points (`django-crontab` /
  `django-background-tasks`), separate from the per-site crawler scripts
  above.
- `utilities/word_frequency.py` — `WordFrequency.get_frequent_words()`, a
  word-cloud generator used to populate `Article.wordcloud_words` /
  `wordcloud_scores`. Tokenizes with a plain regex + `wordcloud`'s stopword
  list, not nltk -- an unused `from nltk import word_tokenize` import (nltk
  isn't even in `requirements.txt`) used to make this module fail to import
  at all; removed.
- `onetimers/`, `custom_scripts/` — one-off maintenance scripts (dedup,
  backfill), not part of the running app; run manually via Django shell when
  needed, not on a schedule.
- `/analytics/` is `django-silk`'s request-profiling UI, wired directly into
  `derrick/urls.py`.

## Conventions

- Views are function-based (`@api_view`), not DRF class-based views/viewsets
  — the commented-out `DefaultRouter` registration in `urls.py` is dead code
  from an earlier approach, not a pattern in use.
- Tests live under `api/tests.py`, covering `word_frequency` plus the
  `api/views.py` endpoints (auth requirement, pagination edge case, keyword
  filter, search-backend failure handling — see "Bugs fixed" below for what
  each of those tests guards against). There is still no coverage for the
  crawler scripts (`custom_crawlers/`) or Celery tasks — add tests when
  touching those.
- `debug_toolbar` is in `MIDDLEWARE` but its URLs are only registered in
  `derrick/urls.py` when `settings.DEBUG` is true (standard django-debug-
  toolbar setup) — this was previously missing entirely (see "Bugs fixed").

## Bugs fixed (2026-08 hardening pass)

- **`search_articles_by_keyword`** referenced `serializer` outside the
  `try` block; an Elasticsearch failure inside the `try` raised an
  unrelated `UnboundLocalError` (crash) instead of a clean error response.
  Now returns HTTP 500 with a `detail` message on failure.
- **`get_articles_by_page`** 404'd on the last, partial page of results
  (e.g. 15 articles, page 2 of size 10 -- `end=20 > 15` triggered 404 even
  though articles 10-14 exist). Now only 404s when the page has zero
  articles (`start >= count`).
- **`get_articles_by_keyword`** loaded every `Article` row into Python and
  did a case-sensitive substring check in a loop. Replaced with a single
  `Article.objects.filter(title__icontains=keyword)` DB query.
- **`test_endpoint`** had a `try/except` that just re-raised the same
  exception (a no-op) — simplified to a direct return.
- **Missing `debug_toolbar` URLs** (see above) meant any request with
  `DEBUG=True` 500'd with `NoReverseMatch: 'djdt' is not a registered
  namespace` — dormant in production since `DEBUG` was previously
  hardcoded `False`, but broke as soon as `DJANGO_DEBUG=1` was exercised
  while fixing the hardcoded-secrets issue. Fixed by registering
  `debug_toolbar.urls` under `__debug__/` when `DEBUG` is on.

## Dependency remediation (2026-08)

`requirements.txt` would not even `pip install` under a modern pip
(`django-elasticsearch-dsl==7.1.1` has non-standard, rejected metadata) --
bumped to `7.4` (still targets the ES7 API this app uses). `pip-audit`
against the original pins found 66 known CVEs across 12 packages; bumped
the ones that don't require a Django major-version jump: `certifi`,
`idna`, `urllib3`, `requests`, `Jinja2` + `MarkupSafe` (transitive-only,
not imported by app code), `Pygments`, `soupsieve`, `sqlparse`, `gunicorn`,
`Pillow`, and `djangorestframework` (bumped to `3.14.0`, the last version
still compatible with `Django==3.1.14` — `3.15+` requires `Django>=4.2`).

**Not fixed, and the single biggest remaining risk:** `Django==3.1.14`
itself is long past EOL and has multiple unpatched CVEs whose fixes only
ship in Django 4.2+/5.x. Reaching a fully patched Django requires a
multi-major-version upgrade (3.1 -> at least 4.2 LTS), which also forces
`djangorestframework` to 3.15+ and needs every other Django-coupled
dependency (`django-cors-headers`, `django-crontab`, `django-silk`,
`django-debug-toolbar`, `django-elasticsearch-dsl`, `django-background-tasks`)
re-verified against the new Django version. That's a real migration, not a
pin bump — it needs a proper test pass against live Postgres +
Elasticsearch + Redis/Celery (none of which were assumed available when
this pass was done) before landing on the production deployment, so it
was deliberately left as a follow-up rather than done blind.
