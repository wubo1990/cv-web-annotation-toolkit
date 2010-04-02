from celery.task import PeriodicTask
from celery.registry import tasks
from datetime import timedelta

import models
import views

class SessionSyncTask(PeriodicTask):
    run_every = timedelta(seconds=311)

    def run(self, **kwargs):
        logger = self.get_logger(**kwargs)
        logger.info("Running session sync!")
        for session in models.Session.objects.all():
            logger.info("Updating session state:" + session.code)
            views.update_session_state(session)


class SubmissionStateSyncTask(PeriodicTask):
    run_every = timedelta(seconds=327)

    def run(self, **kwargs):
        logger = self.get_logger(**kwargs)
        logger.info("Running submission state sync!")
        for session in models.Session.objects.all():
            logger.info("Updating session state:" + session.code)
            views.update_submission_states(session)

tasks.register(SubmissionStateSyncTask)
tasks.register(SessionSyncTask)
