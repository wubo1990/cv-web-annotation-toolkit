from django.conf.urls.defaults import *

import views

urlpatterns = patterns('',


    (r'^upload/$', 'evaluation.views.upload_submission'),
#                                             (r'^upload/(?P<challenge_name>[\w\-]+)/$', 'evaluation.views.upload_submission'),

    #(r'^results/(?P<challenge_name>[\w\-]+)/$', 'evaluation.views.show_best_results'),
    #(r'^results/(?P<challenge_name>[\w\-]+)/all/$', 'evaluation.views.show_all_results'),

    (r'^all_submissions/$', 'evaluation.views.show_all_submissions'),
    (r'^all_submissions/(?P<challenge_name>[\w\-]+)/$', 'evaluation.views.show_all_submissions'),
    (r'^my_submissions/$', 'evaluation.views.show_my_submissions'),
    (r'^my_submissions/(?P<challenge_name>[\w\-]+)/$', 'evaluation.views.show_my_submissions'),
    (r'^view_submission/(?P<submission_id>[\w\-]+)/$', 'evaluation.views.show_submission'),


)
