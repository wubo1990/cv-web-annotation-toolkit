from django.conf.urls.defaults import *

import views

urlpatterns = patterns('',

    (r'^upload/(?P<session_code>[\w\-]+)/video/$', 'mturk.protocols.video_events.views.upload_video'),

);
                       
