#!/usr/bin/env python3
"""
System Status Check Script
Verifies the Django backend configuration and dependencies.
Run this script to check if the backend is properly set up.
"""

import sys
import os

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 6:
        print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python version: {version.major}.{version.minor}.{version.micro} (requires 3.6+)")
        return False

def check_django_installed():
    """Check if Django is installed."""
    try:
        import django
        try:
            version = django.get_version()
        except AttributeError:
            version = django.VERSION
        print(f"✅ Django installed: {version}")
        return True
    except ImportError:
        print("❌ Django not installed")
        return False

def check_rest_framework():
    """Check if Django REST Framework is installed."""
    try:
        import rest_framework
        print(f"✅ Django REST Framework installed")
        return True
    except ImportError:
        print("❌ Django REST Framework not installed")
        return False

def check_beautifulsoup():
    """Check if BeautifulSoup is installed."""
    try:
        import bs4
        print(f"✅ BeautifulSoup4 installed")
        return True
    except ImportError:
        print("❌ BeautifulSoup4 not installed")
        return False

def check_elasticsearch():
    """Check if Elasticsearch library is installed."""
    try:
        import elasticsearch
        print(f"✅ Elasticsearch library installed")
        return True
    except ImportError:
        print("❌ Elasticsearch library not installed")
        return False

def check_celery():
    """Check if Celery is installed."""
    try:
        import celery
        print(f"✅ Celery installed")
        return True
    except ImportError:
        print("❌ Celery not installed")
        return False

def check_nltk():
    """Check if NLTK is installed."""
    try:
        import nltk
        print(f"✅ NLTK installed")
        return True
    except ImportError:
        print("❌ NLTK not installed")
        return False

def check_project_structure():
    """Check if Django project structure exists."""
    django_dir = os.path.join(os.path.dirname(__file__), 'django', 'derrick')
    manage_py = os.path.join(django_dir, 'manage.py')
    
    if os.path.exists(manage_py):
        print(f"✅ Django project structure found")
        return True
    else:
        print(f"❌ Django project structure not found")
        return False

def check_requirements_file():
    """Check if requirements.txt exists."""
    req_file = os.path.join(os.path.dirname(__file__), 'django', 'derrick', 'requirements.txt')
    
    if os.path.exists(req_file):
        print(f"✅ Requirements file found")
        return True
    else:
        print(f"❌ Requirements file not found")
        return False

def main():
    """Run all checks."""
    print("=" * 60)
    print("Web Scraping Backend - System Status Check")
    print("=" * 60)
    print()
    
    checks = [
        ("Python Version", check_python_version),
        ("Project Structure", check_project_structure),
        ("Requirements File", check_requirements_file),
        ("Django", check_django_installed),
        ("Django REST Framework", check_rest_framework),
        ("BeautifulSoup4", check_beautifulsoup),
        ("Elasticsearch", check_elasticsearch),
        ("Celery", check_celery),
        ("NLTK", check_nltk),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append(result)
        except Exception as e:
            print(f"❌ {name}: Error - {str(e)}")
            results.append(False)
        print()
    
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Status: {passed}/{total} checks passed")
    print("=" * 60)
    print()
    
    if passed == total:
        print("🎉 All checks passed! The backend is properly configured.")
        print()
        print("Next steps:")
        print("1. Configure database settings in django/derrick/derrick/settings.py")
        print("2. Run migrations: cd django/derrick && python manage.py migrate")
        print("3. Create superuser: python manage.py createsuperuser")
        print("4. Start server: python manage.py runserver 0.0.0.0:80")
    elif passed >= 3:
        print("⚠️  Basic structure is present but dependencies need installation.")
        print()
        print("To install dependencies:")
        print("1. Run: ./setup.sh")
        print("   OR")
        print("2. pip install -r django/derrick/requirements.txt")
    else:
        print("❌ Critical issues detected. Please check the project setup.")
        print()
        print("To set up the project:")
        print("1. Clone the repository")
        print("2. Run: ./setup.sh")
        print("3. Follow the setup instructions in django/derrick/README.MD")
    
    print()
    print("For more information, see:")
    print("- STATUS.md - Software status and functionality")
    print("- ARCHITECTURE.md - System architecture")
    print("- django/derrick/README.MD - Detailed setup guide")
    print()
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
