from celery.task.schedules import crontab
from celery.decorators import periodic_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

# DataCenterKnowledge
from custom_crawlers.datacenterknowledge.cron_job_homepage_scraper import scraper_datacenter

@periodic_task(
    run_every=(crontab(minute=0, hour='*/6')),
    name="scrape_data_from_site",
    ignore_result=True
)
def scrape_data_from_site():
    """
    Runs all the Scrapers
    """
    # save_latest_flickr_image()
    scraper_datacenter()
    #scraper_start_scraping_xyz()
    logger.info("Scraping task started...")


@periodic_task(
    run_every=(crontab()),
    name="heartbeat",
    ignore_result=True
)
def celery_heartbeat():
    logger.info("Heartbeat sent.")
