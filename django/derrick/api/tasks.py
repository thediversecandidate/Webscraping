from celery.task.schedules import crontab
from celery.decorators import periodic_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

# DataCenterKnowledge
from custom_crawlers.datacenterknowledge.cron_job_homepage_scraper import scraper_datacenter as datacenterknowledge_scraper

# DataCenterFrontier
from custom_crawlers.datacenterfrontier.cron_job_homepage_scraper import scraper_datacenter as datacenterfrontier_scraper

@periodic_task(
    run_every=(crontab(minute=0, hour='*/6')),
    name="scrape_datacenter",
    ignore_result=True
)
def run_datacenterknowledge_scraper():
    """
    Runs the scraper
    """

    # DataCenterKnowledge
    datacenterknowledge_scraper()

@periodic_task(
    run_every=(crontab(minute=0, hour='*/6')),
    name="scrape_datacenter",
    ignore_result=True
)
def run_datacenterfrontier_scraper():
    """
    Runs the scraper
    """
    
    # DataCenterFrontier
    datacenterfrontier_scraper()

    logger.info("Scraping task started...")


@periodic_task(
    run_every=(crontab()),
    name="heartbeat",
    ignore_result=True
)
def celery_heartbeat():
    logger.info("Heartbeat sent.")
