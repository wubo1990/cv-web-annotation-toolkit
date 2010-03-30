from celery.task import PeriodicTask
from celery.registry import tasks
from datetime import timedelta

import models
import views

class SessionSyncTask(PeriodicTask):
    run_every = timedelta(seconds=300)

    def run(self, **kwargs):
        logger = self.get_logger(**kwargs)
        logger.info("Running session sync!")
        for session in models.Session.objects.all():
            logger.info("Updating session state:" + session.code)
            views.update_session_state(session)

tasks.register(SessionSyncTask)
