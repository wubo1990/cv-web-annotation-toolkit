from django.conf.urls.defaults import *

import views

urlpatterns = patterns('',

    (r'^upload/(?P<session_code>[\w\-]+)/image/$', 'mturk.protocols.gxml.views.upload_image'),
    (r'^upload/(?P<session_code>[\w\-]+)/image_tgz/$', 'mturk.protocols.gxml.views.upload_image_tgz'),

    (r'^create_download/(?P<session_code>[\w\-]+)/pack/$', 'mturk.protocols.gxml.views.create_full_pack_download'),

    (r'^create_download/(?P<session_code>[\w\-]+)/xml_masks/$', 'mturk.protocols.gxml.views.create_xml_masks_download'),

    (r'^create_masks/(?P<session_code>[\w\-]+)/$', 'mturk.protocols.gxml.views.create_masks'),

);
                       
