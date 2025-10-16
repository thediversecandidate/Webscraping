# Frequently Asked Questions (FAQ)

## General Questions

### Q: Is this software working?

**Yes**, this is a fully functional Django REST API backend. The software:
- ✅ Has complete implementation of all core features
- ✅ Includes working API endpoints
- ✅ Contains functional web scraping utilities
- ✅ Has database models and migrations
- ✅ Includes authentication system
- ✅ Has unit tests

**However**, to run it, you need:
- PostgreSQL database configured
- Elasticsearch instance running
- Dependencies installed (`./setup.sh` or `pip install -r django/derrick/requirements.txt`)
- Proper environment configuration

### Q: Is this the backend to another software in the repo?

**No, this IS the backend.** The frontend is in a **separate repository**:
- **Frontend Repo**: [thediversecandidate/webscraper-React-FrontEnd](https://github.com/thediversecandidate/webscraper-React-FrontEnd)
- **Technology**: React + TypeScript
- **Purpose**: User interface for browsing and searching scraped articles

This repository contains only the backend API that the frontend consumes.

### Q: What does this software do?

This backend provides:
1. **Web Scraping**: Automated crawlers for tech news websites
2. **Data Storage**: PostgreSQL database for article storage
3. **Search**: Elasticsearch integration for full-text search
4. **REST API**: JSON endpoints for article retrieval and search
5. **Word Cloud Data**: Generate word frequency for visualizations
6. **Background Tasks**: Celery for async scraping jobs

## Setup Questions

### Q: How do I get this running?

```bash
# 1. Setup environment
./setup.sh

# 2. Configure database (edit django/derrick/derrick/settings.py)
# Set your PostgreSQL and Elasticsearch connection strings

# 3. Run migrations
cd django/derrick
python manage.py migrate

# 4. Create admin user
python manage.py createsuperuser

# 5. Start server
python manage.py runserver 0.0.0.0:80
```

### Q: What are the system requirements?

**Required:**
- Python 3.6+
- PostgreSQL database
- Elasticsearch 7.x
- Redis (for Celery task queue)

**Python Dependencies:**
- Django 3.1.14
- Django REST Framework 3.11.2
- BeautifulSoup4 4.9.1
- Elasticsearch 7.7.1
- Celery 5.2.2
- See `django/derrick/requirements.txt` for complete list

### Q: How do I check if my environment is configured correctly?

Run the status check script:
```bash
python3 check_status.py
```

This will verify:
- Python version
- Project structure
- Installed dependencies
- Configuration status

## Usage Questions

### Q: How do I access the API?

1. **Start the server**: `python manage.py runserver`
2. **Get an auth token**: 
   - Login to admin panel: http://localhost:8000/admin
   - Create token in auth tokens section
3. **Make API calls** with header: `Authorization: Token <your-token>`

Example:
```bash
curl -H "Authorization: Token abc123..." \
     http://localhost:8000/articles/page/1/
```

### Q: What API endpoints are available?

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/` | GET | No | Health check |
| `/admin/` | GET | Admin | Django admin |
| `/analytics/` | GET | Yes | Analytics dashboard |
| `/articles/page/<num>/` | GET | Yes | Paginated articles |
| `/articles/keyword/<word>` | GET | Yes | Keyword search |
| `/articles/search/<keyword>/<first>/<count>/<sort>` | GET | Yes | Advanced search |
| `/articles/results/<keyword>` | GET | Yes | Result count |

See [ARCHITECTURE.md](ARCHITECTURE.md) for complete details.

### Q: How do I add a new website to scrape?

1. Copy an existing scraper from `custom_crawlers/`
2. Rename folder to your target website
3. Modify `crawl_for_links.py` for the site structure
4. Update `scrape_article_body_and_save_to_db.py`
5. Run via Django shell

See detailed instructions in [django/derrick/README.MD](django/derrick/README.MD).

## Architecture Questions

### Q: How does the frontend connect to this backend?

```
Frontend (React)
    ↓ HTTP/HTTPS
    ↓ REST API calls
    ↓ Token Authentication
Backend (Django) ← This Repo
    ↓
Database (PostgreSQL + Elasticsearch)
```

The frontend makes HTTP requests to the API endpoints with token authentication.

### Q: What databases are used?

**PostgreSQL** - Primary data storage:
- Stores all article data
- Handles relational queries
- Provides data persistence

**Elasticsearch** - Search engine:
- Full-text search indexing
- Fast keyword searches
- Article ranking and sorting

### Q: How are articles scraped?

1. **CRON jobs** trigger scraping tasks periodically
2. **Celery workers** process scraping jobs asynchronously
3. **BeautifulSoup** parses HTML from target websites
4. **Article data** is extracted and saved to PostgreSQL
5. **Elasticsearch** auto-indexes new articles for search

## Testing Questions

### Q: How do I run tests?

```bash
cd django/derrick
python manage.py test api --verbosity 2
```

### Q: What tests are included?

Currently includes:
- Word frequency utility tests
- Unit tests for core functionality

You can add more tests in `django/derrick/api/tests.py`.

## Deployment Questions

### Q: Where is this deployed?

Production deployment:
- **API**: https://api.thediversecandidate.com
- **Admin**: https://api.thediversecandidate.com/admin
- **Analytics**: https://api.thediversecandidate.com/analytics/

### Q: How do I deploy this?

The application uses:
- **Gunicorn** as WSGI server
- **PostgreSQL** for database
- **Elasticsearch** for search
- **Redis** for Celery
- **Nginx** (likely) as reverse proxy

Configuration files in the `supervisor/` directory.

## Troubleshooting

### Q: I get "Django not installed" error

Run the setup:
```bash
./setup.sh
```

Or manually install:
```bash
pip install -r django/derrick/requirements.txt
```

### Q: Database connection errors

Check your database configuration in:
```
django/derrick/derrick/settings.py
```

Ensure PostgreSQL is running and connection details are correct.

### Q: Elasticsearch connection errors

1. Verify Elasticsearch is running
2. Check connection settings in `settings.py`
3. Ensure Elasticsearch version matches (7.x)

### Q: Import errors when running tests

Make sure you're in the correct directory:
```bash
cd django/derrick
python manage.py test api
```

And that all dependencies are installed.

## Related Resources

- **[STATUS.md](STATUS.md)** - Software status and overview
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture
- **[Django README](django/derrick/README.MD)** - Detailed setup guide
- **[Frontend Repo](https://github.com/thediversecandidate/webscraper-React-FrontEnd)** - React frontend

## Still Have Questions?

1. Check the documentation files listed above
2. Review the code in `django/derrick/`
3. Examine existing scrapers in `custom_crawlers/`
4. Open an issue on GitHub
