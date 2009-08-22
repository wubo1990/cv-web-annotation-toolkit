from django.conf.urls.defaults import *

import views

urlpatterns = patterns('',

    (r'^$', 'autograding.views.main'),

    (r'^apply_auto_grades/(?P<session_code>[\w\-]+)/$', 'autograding.views.grade_session_with_automatic_model'),
    (r'^deactivate_auto_grades/(?P<session_code>[\w\-]+)/$', 'autograding.views.deactivate_autmatic_grades'),
    (r'^activate_auto_grades/(?P<session_code>[\w\-]+)/$', 'autograding.views.activate_autmatic_grades'),

    (r'^build_model_from_session/(?P<session_code>[\w\-]+)/$', 'autograding.views.build_model_from_session'),

);
