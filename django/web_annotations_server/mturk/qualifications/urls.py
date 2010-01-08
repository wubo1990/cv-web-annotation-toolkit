from django.conf.urls.defaults import *
from django.conf import settings

import os

import views

urlpatterns = patterns('',

    (r'^$', 'mturk.qualifications.views.main'),
    #(r'^dashboard/', include('mturk.dashboard.urls')),

    (r'^create/(?P<session_code>[\w\-]+)/(?P<qualification_name>[\w \.\-]+)/$', 'mturk.qualifications.views.create_qualification'),
    (r'^update/(?P<session_code>[\w\-]+)/(?P<qualification_name>[\w \.\-]+)/$', 'mturk.qualifications.views.update_qualification'),

    (r'^show/(?P<qualification_def_name>[\w 0-9\.\-]+)/question/$', 'mturk.qualifications.views.question_xml'),
    (r'^show/(?P<qualification_def_name>[\w 0-9\.\-]+)/answer/$', 'mturk.qualifications.views.answer_xml'),

    (r'^create_automatic_qualifications/(?P<funding_account>[\w 0-9\.\-]+)/$', 'mturk.qualifications.views.create_qualifications_for_worker_metrics'),
    (r'^assign_qualifications_to_workers/(?P<funding_account>[\w 0-9\.\-]+)/$', 'mturk.qualifications.views.assign_qualifications_to_workers'),

    (r'^update_internal_qualifications/$', 'mturk.qualifications.views.update_internal_qualifications'),


);
                       
