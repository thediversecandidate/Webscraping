# Architecture Documentation

## System Overview

This repository contains the **backend API service** for The Diverse Candidate's web scraping platform.

## Component Relationship

### This Repository: Backend API
- **Name**: Webscraping (Django REST API)
- **Role**: Data collection, storage, and API service
- **Technology**: Python, Django, Django REST Framework
- **Port**: 80 (production: api.thediversecandidate.com)

### Frontend Repository
- **Name**: webscraper-React-FrontEnd
- **Role**: User interface for browsing and searching articles
- **Technology**: React, TypeScript
- **Integration**: Consumes REST API from this backend

## Data Flow

```
┌──────────────────────────────────────────────────────────────┐
│                      WEB SCRAPING                            │
│  Custom Crawlers (BeautifulSoup)                             │
│  - DataCenterFrontier                                        │
│  - DataCenterKnowledge                                       │
│  - NetworkWorld                                              │
└─────────────────────┬────────────────────────────────────────┘
                      │
                      ↓ Save articles
┌─────────────────────────────────────────────────────────────┐
│                   DJANGO BACKEND (This Repo)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Models     │  │   Views      │  │  Serializers │      │
│  │   Article    │→ │   REST API   │→ │   JSON       │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
│  Word Frequency Module → Generate word cloud data            │
└─────────────────────┬────────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        ↓             ↓             ↓
┌─────────────┐ ┌─────────────┐ ┌──────────────────┐
│ PostgreSQL  │ │Elasticsearch│ │  REST API        │
│  Database   │ │   Search    │ │  (Token Auth)    │
│             │ │   Index     │ │                  │
└─────────────┘ └─────────────┘ └────────┬─────────┘
                                          │
                                          ↓
                               ┌──────────────────────┐
                               │  React Frontend      │
                               │  (Separate Repo)     │
                               │  - View Articles     │
                               │  - Search Articles   │
                               │  - Word Clouds       │
                               └──────────────────────┘
```

## API Endpoints

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/` | GET | No | Health check |
| `/admin/` | GET | Yes (Django Admin) | Admin dashboard |
| `/analytics/` | GET | Yes | Performance analytics |
| `/articles/page/<page_num>/` | GET | Yes | Get paginated articles |
| `/articles/keyword/<keyword>` | GET | Yes | Search by keyword in title |
| `/articles/search/<keyword>/<first>/<no_of_results>/<sort_by>` | GET | Yes | Advanced search with Elasticsearch |
| `/articles/results/<keyword>` | GET | Yes | Get total count of search results |

## Database Schema

### Article Model
```python
class Article:
    title: CharField(max_length=250, unique=True)
    url: CharField(max_length=250, unique=True)
    body: TextField()
    article_summary: TextField()
    list_of_keywords: TextField()
    wordcloud_words: TextField()
    wordcloud_scores: TextField()
    created_date: DateTimeField()
    published_date: DateTimeField()
```

## Background Tasks

### CRON Jobs
- Automated scraping tasks run periodically
- Managed by `django-crontab`
- Background task processing with Celery

### Task Queue
- Celery workers process scraping tasks
- Redis as message broker
- Allows asynchronous article processing

## Deployment Architecture

### Production Environment
```
                    Internet
                       │
                       ↓
              ┌────────────────┐
              │  Load Balancer │
              └────────┬───────┘
                       │
          ┌────────────┴────────────┐
          ↓                         ↓
  ┌──────────────┐         ┌──────────────┐
  │   Django     │         │   Frontend   │
  │   Gunicorn   │         │   Server     │
  │ (Port 80)    │         │              │
  └──────┬───────┘         └──────────────┘
         │
    ┌────┴──────┐
    ↓           ↓
┌────────┐  ┌─────────────┐
│PostGres│  │Elasticsearch│
└────────┘  └─────────────┘
```

### Key Configuration
- **Web Server**: Gunicorn
- **Database**: PostgreSQL (psycopg2-binary)
- **Search**: Elasticsearch 7.7.1
- **Task Queue**: Celery + Redis
- **Monitoring**: Django Silk (performance profiling)

## Security

### Authentication
- Token-based authentication (Django REST Framework)
- Tokens managed via Django admin
- All article endpoints require authentication

### Configuration
- Secret keys in settings
- DEBUG=False in production
- Allowed hosts restricted to known domains

## Development Workflow

### Adding New Scrapers
1. Copy existing scraper folder from `custom_crawlers/`
2. Rename to target website
3. Modify `crawl_for_links.py` for site structure
4. Update `scrape_article_body_and_save_to_db.py`
5. Run scraper via Django shell
6. Articles automatically indexed in Elasticsearch

### Testing
```bash
# Setup environment
./setup.sh

# Run tests
cd django/derrick
python manage.py test api --verbosity 2
```

## Technology Stack Summary

| Layer | Technology | Version |
|-------|------------|---------|
| Framework | Django | 3.1.14 |
| API | Django REST Framework | 3.11.2 |
| Database | PostgreSQL | (via psycopg2) |
| Search | Elasticsearch | 7.7.1 |
| Scraping | BeautifulSoup4 | 4.9.1 |
| Task Queue | Celery | 5.2.2 |
| Web Server | Gunicorn | 20.0.4 |
| Language | Python | 3.x |

## Integration Points

### With Frontend
- REST API over HTTPS
- JSON responses
- Token authentication in headers
- CORS enabled for cross-origin requests

### With External Services
- Web scraping targets (various tech news sites)
- Elasticsearch for search indexing
- PostgreSQL for data persistence
- Redis for task queue
