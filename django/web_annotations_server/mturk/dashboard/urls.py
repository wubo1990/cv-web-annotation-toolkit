from django.conf.urls.defaults import *

import views

urlpatterns = patterns('',

    (r'^session/(?P<session_code>[\w\-]+)/$', 'mturk.dashboard.views.session_dashboard'),

    (r'^worker_internal/(?P<worker_id>[\w\-]+)/$', 'mturk.dashboard.views.worker_internal_dashboard'),
);
