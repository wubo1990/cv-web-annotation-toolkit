from django.conf.urls.defaults import *

import views

urlpatterns = patterns('',

    (r'^create_download/(?P<session_code>[\w\-]+)/raw_xml/$', 'mturk.protocols.attributes.views.create_raw_xml_download'),

);
                       
