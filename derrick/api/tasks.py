from celery.task.schedules import crontab
from celery.decorators import periodic_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

from api.scraper_utils import scraper_datacenter

@periodic_task(
    run_every=(crontab(minute=0, hour='*/6')),
    name="scrape_data_from_site",
    ignore_result=True
)
def scrape_data_from_site():
    """
    Saves latest image from Flickr
    """
    # save_latest_flickr_image()
    scraper_datacenter()
    logger.info("Scraping task started...")
