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
python manage.py runserver 0.0.0.0:80
python manage.py test api --verbosity 2      # test suite (api app only)
```

Needs Postgres and Elasticsearch reachable per `derrick/settings.py`, and
Redis + Celery for the async task queue (`derrick/celery.py`,
`supervisor/derrick_celery.conf`, `supervisor/derrick_celerybeat.conf`).
`rebuild_elastic_index.sh` / `restart_server.sh` / `status.sh` are the
deploy-time operational scripts (not part of the test loop).

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
- `utilities/word_frequency.py` — `WordFrequency.get_frequent_words()`, an
  nltk-based word-cloud generator used to populate `Article.wordcloud_words`
  / `wordcloud_scores`. This is the one utility with real test coverage
  (`api/tests.py`).
- `onetimers/`, `custom_scripts/` — one-off maintenance scripts (dedup,
  backfill), not part of the running app; run manually via Django shell when
  needed, not on a schedule.
- `/analytics/` is `django-silk`'s request-profiling UI, wired directly into
  `derrick/urls.py`.

## Conventions

- Views are function-based (`@api_view`), not DRF class-based views/viewsets
  — the commented-out `DefaultRouter` registration in `urls.py` is dead code
  from an earlier approach, not a pattern in use.
- Tests live under `api/tests.py`; the only real suite covers
  `utilities/word_frequency.py`. There is no test coverage for the
  crawlers, views, or models — add tests when touching those rather than
  assuming existing coverage.
