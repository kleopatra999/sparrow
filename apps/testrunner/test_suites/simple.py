# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
import ujson
from celery import group
from celery.utils.log import get_task_logger

from testrunner.tasks.deploy import Deploy
from testrunner.tasks.http_get import HttpGet
from testrunner.tasks.http_get import MWProfilerGet
from testrunner.tasks.phantomas_get import PhantomasGet
from testrunner.tasks.process_results import ProcessResponses
from testrunner.tasks.selenium_get import SeleniumGet

logger = get_task_logger(__name__)


class SimpleTestSuite(object):
    DEFAULT_RETRIES_COUNT = 10

    def __init__(self, *args, **kwargs):
        self.DEPLOY_HOST = settings.DEPLOYTOOLS_MASTER
        self.TARGET_ENV = settings.TEST_TARGET_HOSTS[0]

    def run(self, **kwargs):
        retries = kwargs.pop('retries')
        if retries is None:
            retries = self.DEFAULT_RETRIES_COUNT

        logger.info('Started execution of task #{} (x{})'.format(kwargs['task_uri'], retries))
        logger.debug('params = ' + ujson.dumps(kwargs))

        tasks = (
            Deploy().s(
                deploy_host=self.DEPLOY_HOST,
                app='wikia',
                env=self.TARGET_ENV,
                repos={
                    'app': kwargs['app_commit'],
                    'config': kwargs['config_commit']
                }
            ) |
            group(
                HttpGet().si(url=kwargs['url'], retries=retries),
                MWProfilerGet().si(url=kwargs['url'], retries=retries),
                SeleniumGet().si(url=kwargs['url'], retries=retries),
                PhantomasGet().si(url=kwargs['url'], retries=retries)
            ) |
            ProcessResponses().s(
                result_uri=kwargs['result_uri'],
                task_uri=kwargs['task_uri'],
                test_run_uri=kwargs['test_run_uri']
            )
        )

        result = tasks.delay()

        logger.info('Scheduled execution of task #{0}: {1}'.format(kwargs['task_uri'], result.id))

        return result
