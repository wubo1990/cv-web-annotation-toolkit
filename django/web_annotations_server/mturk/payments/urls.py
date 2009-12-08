from django.conf.urls.defaults import *
from django.conf import settings

import os

import views

urlpatterns = patterns('',
    (r'^$', 'mturk.payments.views.main'),
    (r'^create/interactive/$', 'mturk.payments.views.create_interactive'),
    (r'^create/simple/(?P<work_product_id>[\w\-]+)/$', 'mturk.payments.views.create_simple'),
    (r'^create/simple2/(?P<worker>[\w\-]+)/(?P<session_code>[\w\-]+)/$', 'mturk.payments.views.create_simple2'),
);

