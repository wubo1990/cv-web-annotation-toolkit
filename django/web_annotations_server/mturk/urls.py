from django.conf.urls.defaults import *
from django.conf import settings

import os

import views
import dashboard.views

urlpatterns = patterns('',

    (r'^$', 'mturk.views.main'),
    (r'^all/$', 'mturk.views.main_all'),
    (r'^index/$', 'mturk.views.main'),

    (r'^dashboard/', include('mturk.dashboard.urls')),

    (r'^(?P<protocol>[\w-]+)/(?P<session_code>[\w\-]+)/task.html', 'mturk.views.showtask'),





    (r'^get_task/(?P<session_code>[\w\-]+)/', 'mturk.views.showtask'),
    (r'^submit/', 'mturk.views.submit_result'),


    (r'^submission_data_xml/(?P<id>\d+)/(?P<ext_hitid>[\w\-]+)/$', 'mturk.views.get_submission_data_xml'),

    (r'^random_results/(?P<session_code>[\w\-]+)/', 'mturk.views.show_random_results'),

    (r'^show_most_recent_result/(?P<session_code>[\w\-]+)/$', 'mturk.views.show_most_recent_result'),
    (r'^results/$', 'mturk.views.show_sessions'),
    (r'^results/(?P<session_code>[\w\-]+)/$', 'mturk.views.show_paged_results_base'),
    (r'^results/(?P<session_code>[\w\-]+)/p(?P<page>[0-9]+)/$', 'mturk.views.show_paged_results'),
    (r'^good_results/(?P<session_code>[\w\-]+)/$', 'mturk.views.show_good_results_paged_base'),
    (r'^good_results/(?P<session_code>[\w\-]+)/p(?P<page>[0-9]+)/$', 'mturk.views.show_good_results_paged'),

    (r'^good_results_w_filter/(?P<session_code>[\w\-]+)/p(?P<page>[0-9]+)/(?P<filter>.*)/$', 
         'mturk.views.show_good_results_w_filter_paged'),


    (r'^resubmit_bad_results/(?P<session_code>[\w\-]+)/$', 'mturk.views.submit_redo_HITs'),

    (r'^good_results/(?P<session_code>[\w\-]+)/big/p(?P<page>[0-9]+)/$', 'mturk.views.show_good_results_paged',
     {'num_per_page':10,'template_name':'protocols/g-xml/show_list_huge.html'}
     ),
    (r'^good_results/(?P<session_code>[\w\-]+)/small/p(?P<page>[0-9]+)/$', 'mturk.views.show_good_results_paged',
     {'num_per_page':3,'template_name':'protocols/g-xml/show_list_huge.html'}
     ),

    (r'^ordered_results/(?P<order_by>[\w\-]+)/(?P<session_code>[\w\-]+)/$', 'mturk.views.show_paged_results_base'),
    (r'^ordered_results/(?P<order_by>[\w\-\.]+)/(?P<session_code>[\w\-]+)/p(?P<page>[0-9]+)/$', 'mturk.views.show_paged_results'),


    (r'^result_stats/(?P<session_code>[\w\-]+)/by_worker/$', 'mturk.stats.session_stats_by_worker'),


    (r'^grading/(?P<session_code>[\w\-]+)/$', 'mturk.views.grading_paged_base'),
    (r'^grading/(?P<session_code>[\w\-]+)/p(?P<page>[0-9]+)/$', 'mturk.views.grading_paged'),

    (r'^grading/thumbnails_random/(?P<session_code>[\w\-]+)/$', 'mturk.views.grading_thumbnail_random'),

    (r'^grading/by_worker/(?P<session_code>[\w\-]+)/(?P<worker_code>[\w\-]+)/$', 'mturk.views.grading_by_worker_paged_base'),
    (r'^grading/by_worker/(?P<session_code>[\w\-]+)/(?P<worker_code>[\w\-]+)/p(?P<page>[0-9]+)/$', 'mturk.views.grading_by_worker_paged'),
    (r'^grading/by_id/(?P<session_code>[\w\-]+)/(?P<submission_id>[\w\-]+)/$', 'mturk.views.grading_by_submission_id'),
    (r'^grading/conflict/show/(?P<session_code>[\w\-]+)/(?P<grade_1_id>[\w\-]+)/(?P<grade_2_id>[\w\-]+)/$', 'mturk.views.show_grading_conflict_details'),

    (r'^grading/by_worker_no_session/(?P<worker_code>[\w\-]+)/$', 'mturk.views.grading_by_worker_no_session_paged_base'),
    (r'^grading/by_worker_no_session/(?P<worker_code>[\w\-]+)/p(?P<page>[0-9]+)/$', 'mturk.views.grading_by_worker_no_session_paged'),

    (r'^grading/deactivate_grade/(?P<grade_id>[\w\-]+)/$', 'mturk.views.deactivate_grade_record'),

    (r'^grading_submit/(?P<submissionID>[0-9]+)/$', 'mturk.views.grading_submit'),

    (r'^adjudicate/(?P<session_code>[\w\-]+)/(?P<submission_id>[\w\-]+)/$', 'mturk.views.adjudicate_by_submission_id'),
    (r'^adjudicate_submit/(?P<submissionID>[0-9]+)/$', 'mturk.views.adjudicate_submit'),

    (r'^grading_report/(?P<session_code>[\w\-]+)/reject/$', 'mturk.views.grading_report_reject'),
    (r'^grading_report/(?P<session_code>[\w\-]+)/approve/$', 'mturk.views.grading_report_approve'),

    (r'^grading_report/worker/(?P<worker_id>[\w\-]+)/$', 'mturk.views.grading_report_for_worker'),

    (r'^results_report/(?P<session_code>[\w\-]+)/perfect/$', 'mturk.views.get_perfect_results'),
    (r'^results_report/(?P<session_code>[\w\-]+)/non_perfect/$', 'mturk.views.get_non_perfect_results'),

    (r'^newHIT/$', 'mturk.views.newHIT'),
    (r'^newHIT2/$', 'mturk.views.newHIT'),
    (r'^new_HIT_generic/$', 'mturk.views.new_HIT_generic'),
    (r'^copy_session/(?P<prototype_session_code>[\w\-]+)/(?P<new_session_code>[\w\-]+)/$', 'mturk.views.copy_session'),

    (r'^stats/all/$', 'mturk.views.stats_all'),

    (r'^session_hits/(?P<session_code>[\w\-]+)/(?P<hit_state>[0-9]+)/$', 'mturk.views.show_session_hits'),
    (r'^session_hits/(?P<session_code>[\w\-]+)/(?P<hit_state>[0-9]+)/p(?P<page>[0-9+])/$', 'mturk.views.show_session_hits'),


    (r'^hit_results_xml/(?P<ext_id>[\w\-]+)/', 'mturk.views.get_hit_results_xml'),
    (r'^hit_parameters/(?P<ext_id>[\w\-]+)/', 'mturk.views.send_hit_parameters'),
    (r'^task_parameters/(?P<task_name>[\w\-]+)/', 'mturk.views.get_task_parameters'),

    (r'^good_hit_results_xml/(?P<ext_id>[\w\-]+)/', 'mturk.views.get_good_hit_results_xml'),

    (r'^session_images/(?P<session_code>[\w\-]+)/$', 'mturk.views.get_session_images'),
    (r'^session_images/(?P<session_code>[\w\-]+)/wget/$', 'mturk.views.get_session_images_wget'),
    (r'^session_images2/(?P<session_code>[\w\-]+)/$', 'mturk.views.get_session_images2'),
    (r'^session_images3/(?P<session_code>[\w\-]+)/$', 'mturk.views.get_session_images3'),

    (r'^session_good_results_list/(?P<session_code>[\w\-]+)/$', 'mturk.views.get_session_good_results'),

    (r'^reject_worker_all/(?P<worker_id>[\w\-]+)/$', 'mturk.views.reject_worker_all'),

    (r'^reject_poor_results/(?P<session_code>[\w\-]+)/$', 'mturk.views.reject_poor_results'),
    (r'^approve_good_results/(?P<session_code>[\w\-]+)/$', 'mturk.views.approve_good_results'),
    (r'^approve_all_results/(?P<session_code>[\w\-]+)/$', 'mturk.views.approve_all_results'),

    (r'^approve_absoltely_all_results/(?P<magic_code>[\w\-]+)/$', 'mturk.views.approve_absolutely_all_results'),


    (r'^grading/submit/session/(?P<session_code>[\w\-]+)/(?P<grading_session_code>[\w-]+)/$', 'mturk.views.grading_submit_session'),
    #+                   
    (r'^ban_worker/(?P<worker_id>[\w\-]+)/$', 'mturk.views.ban_worker'),

    (r'^expire_session_hits/(?P<session_code>[\w\-]+)/$', 'mturk.views.expire_session_hits'),

    (r'^stats/session_details/(?P<session_code>[\w\-]+)/$', 'mturk.views.stats_session_detail'),

    (r'^internal/create_qualifications/$', 'mturk.views.create_qualifications'),


    (r'^p/video_events/', include('mturk.protocols.video_events.urls')),
    (r'^p/gxml/', include('mturk.protocols.gxml.urls')),


    (r'^download/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.join(settings.DATASETS_ROOT,'downloads')}),

#    (r'^rospublishers/$', 'mturk.views.get_ros_publishers'),
);
                       
