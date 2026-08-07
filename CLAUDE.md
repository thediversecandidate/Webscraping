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

A Django 5.2 LTS REST API (app name `derrick`, project root
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
- `cron_jobs/` — `scraper.py`, the `django-crontab` entry point named by
  the `CRONJOBS` setting. Separate from the per-site crawler scripts above,
  and separate again from the Celery beat schedule (`CELERY_BEAT_SCHEDULE`
  in settings, running the `api/tasks.py` tasks). Note `run_scraping_job()`
  in here is still a stub that only prints — the real scheduled scraping
  path is the Celery one.
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

Found during the Django 5.2 upgrade — all four had been silently broken,
none were caused by the upgrade itself:

- **`custom_crawlers/datacenterfrontier/cron_job_homepage_scraper.py` was
  not valid Python.** Two separate blocks mixed tab and space indentation,
  producing a `TabError` at import. The DataCenterFrontier crawler could
  never have run. Fixed; every `.py` in the project now parses cleanly
  (worth re-checking with a syntax sweep if more crawler folders get
  copy-pasted, since that's how this one likely happened).
- **`api/tasks.py` could not import at all** — it used
  `celery.task.schedules` and `celery.decorators.periodic_task`, both
  removed in Celery 4, against a Celery 5 pin. Rewritten with
  `@shared_task`, with the recurrence moved to `CELERY_BEAT_SCHEDULE`.
- **Both scraper tasks shared the Celery task name `"scrape_datacenter"`**,
  so registering the second silently overwrote the first — DataCenterKnowledge
  would never have been scheduled even once the import was fixed. They now
  use distinct (default, module-derived) names.
- **No Celery setting was actually being applied.** `derrick/celery.py`
  called `config_from_object('django.conf:settings')` with no
  `namespace=`, so Celery 4+ looked for lowercase setting names that don't
  exist here; `BROKER_URL` (the Celery 3 spelling) was ignored entirely and
  the broker silently fell back to the default `amqp://localhost` rather
  than the configured Redis. Fixed with `namespace='CELERY'` and renaming
  `BROKER_URL` → `CELERY_BROKER_URL`. Both broker/backend now also read
  from the environment. `CELERY_TIMEZONE` was `'Africa/Nairobi'` against a
  Django `TIME_ZONE` of `'UTC'` — a 3-hour skew between scheduling and
  timestamps, almost certainly an unintended copy-paste; now set to
  `TIME_ZONE`. **If a non-UTC schedule was actually intended, change both
  together.**

Found in the earlier pass:

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

## Dependency remediation & the Django 5.2 upgrade (2026-08)

`requirements.txt` originally would not even `pip install` under a modern
pip (`django-elasticsearch-dsl==7.1.1` ships non-standard, rejected
metadata), and `pip-audit` found **66 known CVEs across 12 packages**.
The stack has since been migrated off the EOL Django 3.1 line entirely:

**Now on Django 5.2.17 LTS** (supported to April 2028). Note 4.2 LTS was
*also* EOL by the time this was done (April 2026), so 5.2 — not 4.2 — is
the correct target if this is ever redone from scratch. `pip-audit`
against the current pins reports **no known vulnerabilities**.

Constraints that shaped the version choices, worth knowing before bumping
anything further:

- **Elasticsearch stays on the 7.x client** (`elasticsearch==7.17.13`,
  `elasticsearch-dsl==7.4.1`, `django-elasticsearch-dsl==7.4`) because the
  deployed ES *server* is 7.7.1 (see `docker-compose.yml` in the
  `webscraper-React-FrontEnd` repo). Moving to the 8.x client line requires
  upgrading that server first — a real infrastructure change, not a pin
  bump. `elasticsearch==7.17.13` specifically is the version that relaxes
  its `urllib3<2` pin on Python 3.10+, which is what allows `urllib3` to
  reach a patched 2.x here at all.
- **`django-background-tasks` was removed, not upgraded.** It was pinned at
  1.2.5 (dead upstream, depends on the equally dead `django-compat`) and
  blocked the Django upgrade outright. The only code using it —
  `cron_jobs/tasks.py` and `cron_jobs/background_scraper.py` — consisted of
  two demo stubs (`demo_task` logging a string, `notify_user` printing
  "I ran!") that nothing anywhere called. Both files and the
  `'background_task'` INSTALLED_APPS entry were deleted. If deferred
  background work is wanted later, Celery is already wired up for it.
- **`DEFAULT_AUTO_FIELD` is explicitly pinned to `AutoField`**, not Django
  3.2+'s `BigAutoField` default. This is deliberate: it keeps the upgrade
  from generating a migration that alters the primary key column type on
  the existing production `articles` table. `manage.py makemigrations
  --check` reports no changes, i.e. **this upgrade needs no schema
  migration**. Switching to `BigAutoField` is a separate, deliberate call.
