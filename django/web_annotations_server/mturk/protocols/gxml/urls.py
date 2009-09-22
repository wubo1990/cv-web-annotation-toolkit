from django.conf.urls.defaults import *

import views

urlpatterns = patterns('',

    (r'^upload/(?P<session_code>[\w\-]+)/image/$', 'mturk.protocols.gxml.views.upload_image'),

);
                       
