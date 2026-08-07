from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

# DataCenterKnowledge
from custom_crawlers.datacenterknowledge.cron_job_homepage_scraper import scraper_datacenter as datacenterknowledge_scraper

# DataCenterFrontier
from custom_crawlers.datacenterfrontier.cron_job_homepage_scraper import scraper_datacenter as datacenterfrontier_scraper


# Celery 4 removed @periodic_task; the recurring schedule for these lives in
# CELERY_BEAT_SCHEDULE in derrick/settings.py instead. Both tasks previously
# shared the name "scrape_datacenter", so registering the second one silently
# overwrote the first -- datacenterknowledge never ran. They now have
# distinct names (the defaults derived from their module + function path).
@shared_task(ignore_result=True)
def run_datacenterknowledge_scraper():
    """Scrape the DataCenterKnowledge homepage."""
    logger.info("DataCenterKnowledge scrape started.")
    datacenterknowledge_scraper()
    logger.info("DataCenterKnowledge scrape finished.")


@shared_task(ignore_result=True)
def run_datacenterfrontier_scraper():
    """Scrape the DataCenterFrontier homepage."""
    logger.info("DataCenterFrontier scrape started.")
    datacenterfrontier_scraper()
    logger.info("DataCenterFrontier scrape finished.")
