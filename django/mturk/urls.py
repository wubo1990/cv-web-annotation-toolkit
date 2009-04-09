from django.conf.urls.defaults import *

import views

urlpatterns = patterns('',

    (r'^index/', 'mturk.views.index'),

    (r'^(?P<protocol>[\w-]+)/(?P<session_code>[\w\-]+)/task.html', 'mturk.views.showtask'),
    #(r'^(?P<session_code>[\w\-]+)/submit.html', 'mturk.views.report_result'),


    #(r'^new_tasks_full/(?P<k_session>[\w\-]+)/(?P<k_ds>[\w\-]+)/(?P<k_protocol>[\w\-]+)', 'mturk.views.new_tasks_full'),
    (r'^load_tasks/(?P<k_session>[\w\-]+)/', 'mturk.views.load_tasks'),
    (r'^get_task/(?P<session_code>[\w\-]+)/', 'mturk.views.showtask'),
    (r'^get_task_for_hit/(?P<session_code>[\w\-]+)/(?P<hit_int_id>[\w\-]+)/', 'mturk.views.show_task_for_hit'),
    (r'^get_task_for_hit_ext/(?P<session_code>[\w\-]+)/(?P<hit_id>[\w\-]+)/(?P<ext_hitid>[\w\-]+)/$', 'mturk.views.show_task_for_hit_ext'),
    (r'^hit_data/(?P<ext_id>[\w\-]+)/', 'mturk.views.send_hit_data'),
    (r'^submit/', 'mturk.views.submit_result'),

    (r'^submission/(?P<id>\d+)/$', 'mturk.views.view_submission'),
    (r'^view_submission/(?P<id>\d+)/(?P<hitid>[\w\-]+)/$', 'mturk.views.view_submission'),

    (r'^submission_data_xml/(?P<id>\d+)/(?P<ext_hitid>[\w\-]+)/$', 'mturk.views.get_submission_data_xml'),
    (r'^submission_data/(?P<id>\d+)/(?P<ext_hitid>[\w\-]+)/$', 'mturk.views.get_submission_data'),
    (r'^submission_gt_data/(?P<id>\d+)/(?P<ext_hitid>[\w\-]+)/$', 'mturk.views.get_submission_gt_data'),
    #(r'^submission_data/(?P<id>\d+)/$', 'mturk.views.get_submission_data'),
    #(r'^submission_data/', 'mturk.views.get_submission_data'),

    (r'^random_results/(?P<session_code>[\w\-]+)/', 'mturk.views.show_random_results'),

    (r'^show_most_recent_result/(?P<session_code>[\w\-]+)/$', 'mturk.views.show_most_recent_result'),
    (r'^results/$', 'mturk.views.show_sessions'),
    (r'^results/(?P<session_code>[\w\-]+)/$', 'mturk.views.show_paged_results_base'),
    (r'^results/(?P<session_code>[\w\-]+)/p(?P<page>[0-9]+)/$', 'mturk.views.show_paged_results'),
    (r'^ordered_results/(?P<order_by>[\w\-]+)/(?P<session_code>[\w\-]+)/$', 'mturk.views.show_paged_results_base'),
    (r'^ordered_results/(?P<order_by>[\w\-\.]+)/(?P<session_code>[\w\-]+)/p(?P<page>[0-9]+)/$', 'mturk.views.show_paged_results'),

    (r'^results/(?P<session_code>[\w\-]+)/imagelist/$', 'mturk.views.show_results_imagelist'),

    (r'^grading/(?P<session_code>[\w\-]+)/$', 'mturk.views.grading_paged_base'),
    (r'^grading/(?P<session_code>[\w\-]+)/p(?P<page>[0-9]+)/$', 'mturk.views.grading_paged'),

    (r'^grading_submit/(?P<submissionID>[0-9]+)/$', 'mturk.views.grading_submit'),

    (r'^grading_report/(?P<session_code>[\w\-]+)/reject/$', 'mturk.views.grading_report_reject'),
    (r'^grading_report/(?P<session_code>[\w\-]+)/approve/$', 'mturk.views.grading_report_approve'),

    (r'^grading_report/worker/(?P<worker_id>[\w\-]+)/$', 'mturk.views.grading_report_for_worker'),

    (r'^results_report/(?P<session_code>[\w\-]+)/perfect/$', 'mturk.views.get_perfect_results'),
    (r'^results_report/(?P<session_code>[\w\-]+)/non_perfect/$', 'mturk.views.get_non_perfect_results'),

    (r'^newHIT/$', 'mturk.views.newHIT'),
    (r'^newHIT2/$', 'mturk.views.newHIT2'),

    (r'^stats/all/$', 'mturk.views.stats_all'),

    (r'^hit_results_xml/(?P<ext_id>[\w\-]+)/', 'mturk.views.get_hit_results_xml'),

    (r'^session_images/(?P<session_code>[\w\-]+)/$', 'mturk.views.get_session_images'),
    (r'^session_images/(?P<session_code>[\w\-]+)/wget/$', 'mturk.views.get_session_images_wget'),

    (r'^reject_poor_results/(?P<session_code>[\w\-]+)/$', 'mturk.views.reject_poor_results'),
    (r'^approve_good_results/(?P<session_code>[\w\-]+)/$', 'mturk.views.approve_good_results'),
    (r'^approve_all_results/(?P<session_code>[\w\-]+)/$', 'mturk.views.approve_all_results'),

)
