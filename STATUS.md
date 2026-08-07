# Web Scraping Backend - Status and Architecture

## Is this software working?

**Yes, this is a working Django REST API backend** designed to:
- Scrape and collect articles from various data center and technology news websites
- Store articles in a PostgreSQL database with Elasticsearch indexing
- Provide RESTful API endpoints for searching and retrieving articles
- Generate word frequency data for word cloud visualization

## What does this software do?

This is a **Django REST API backend** (version 3.1.14) that serves as the data layer for a web scraping platform. It provides:

### Core Functionality:
1. **Web Scraping**: Automated crawlers that scrape articles from websites including:
   - DataCenterFrontier
   - DataCenterKnowledge
   - NetworkWorld

2. **Data Storage**: Uses PostgreSQL database to store:
   - Article titles and URLs
   - Article body content
   - Article summaries
   - Keywords and word cloud data
   - Published dates

3. **Search Capabilities**: Elasticsearch integration (v7.7.1) for:
   - Full-text search across article content
   - Keyword-based article discovery
   - Sorting by published date

4. **REST API Endpoints**:
   - `GET /` - Health check endpoint (returns "Hello world!")
   - `GET /articles/page/<page_num>/` - Paginated article retrieval (10 per page)
   - `GET /articles/keyword/<keyword>` - Search articles by keyword in title
   - `GET /articles/search/<keyword>/<first>/<no_of_results>/<sort_by>` - Advanced Elasticsearch search
   - `GET /articles/results/<keyword>` - Get total count of results for a keyword
   - `GET /admin/` - Django admin dashboard
   - `GET /analytics/` - Analytics dashboard (django-silk)

5. **Utilities**:
   - Word frequency analysis module for generating word clouds
   - CRON jobs for automated scraping tasks
   - Background task processing with Celery

## Is this the backend to another software in the repo?

**Yes, this is the backend API for a separate frontend application.**

Based on the organization's repositories, this backend serves:

### Frontend Application:
- **Repository**: `thediversecandidate/webscraper-React-FrontEnd`
- **Technology**: TypeScript/React
- **Description**: "FrontEnd Webscraper"
- **Integration**: The frontend consumes this Django REST API to:
  - Display scraped articles to users
  - Generate word clouds from article data
  - Provide search and filtering capabilities

### Architecture Overview:
```
┌─────────────────────────────────────┐
│   React Frontend (TypeScript)       │
│   webscraper-React-FrontEnd repo    │
└────────────────┬────────────────────┘
                 │ HTTP/REST API
                 │ (Token Authentication)
                 ↓
┌─────────────────────────────────────┐
│   Django REST API Backend           │
│   This Repository (Webscraping)     │
│   - Django 3.1.14                   │
│   - Django REST Framework           │
│   - Token Authentication            │
└────────────────┬────────────────────┘
                 │
        ┌────────┴────────┐
        ↓                 ↓
┌───────────────┐  ┌──────────────────┐
│  PostgreSQL   │  │  Elasticsearch   │
│   Database    │  │   Search Index   │
└───────────────┘  └──────────────────┘
```

## Authentication

The API uses **Token-based authentication** (Django REST Framework):
- Header: `Authorization: Token <token>`
- Tokens managed through Django admin dashboard
- Most endpoints require authentication (except index/health check)

## Deployment Information

Based on the configuration:
- **Production URL**: `https://api.thediversecandidate.com`
- **Admin Dashboard**: `https://api.thediversecandidate.com/admin`
- **Analytics**: `https://api.thediversecandidate.com/analytics/`
- **Default Credentials** (from README):
  - Username: `derrick`
  - Password: `derrick`

## Testing

The repository includes:
- Unit tests for the WordFrequency utility
- Test runner: `python manage.py test api --verbosity 2`
- Setup script: `./setup.sh` (creates virtual environment and installs dependencies)

## Key Dependencies

- Django 3.1.14
- Django REST Framework 3.11.2
- Elasticsearch 7.7.1
- BeautifulSoup4 4.9.1 (for web scraping)
- Celery 5.2.2 (background tasks)
- PostgreSQL (via psycopg2-binary)
- NLTK (for text processing)

## Current Status

✅ **Working**: The software has a complete implementation with:
- Functional API endpoints
- Database models
- Web scraping utilities
- Search integration
- Authentication system
- Admin interface

⚠️ **Note**: This is a backend API service that requires:
- PostgreSQL database running
- Elasticsearch instance running
- Proper environment configuration
- The frontend application for end-user interaction

## How to Use

1. **Setup**: Run `./setup.sh` to create virtual environment
2. **Configure**: Set up database and Elasticsearch connections in settings
3. **Run Server**: `python manage.py runserver 0.0.0.0:80`
4. **Access API**: Connect frontend or use API endpoints with token authentication
5. **Add Scrapers**: Follow the guide in `django/derrick/README.MD` to add new site scrapers

## Related Repositories

- **Frontend**: [webscraper-React-FrontEnd](https://github.com/thediversecandidate/webscraper-React-FrontEnd)
- **iOS Apps**: SwiftWebCrawlerUI, ElasticSearchPOC (alternative frontends)
