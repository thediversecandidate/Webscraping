from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'derrick.settings')
app = Celery('derrick')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
# namespace='CELERY' means only settings prefixed CELERY_ are read, with the
# prefix stripped and lowercased (CELERY_BROKER_URL -> broker_url). Without
# it, Celery 4+ looks for lowercase setting names this Django settings
# module never defined, so none of the Celery config was actually applied.
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))