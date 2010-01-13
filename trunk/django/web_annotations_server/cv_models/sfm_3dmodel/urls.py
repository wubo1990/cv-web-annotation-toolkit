from django.conf.urls.defaults import *
from django.conf import settings


urlpatterns = patterns('',

    (r'^$', 'cv_models.views.main'),
    (r'^download/(?P<model_id>[0-9]+)/(?P<object_tag>[\w-]+)/', 'cv_models.views.download_model'),

    (r'^models/$', 'cv_models.sfm_3dmodel.views.show_models'),
    (r'^model/(?P<model_id>[0-9]+)/$', 'cv_models.sfm_3dmodel.views.show_model'),                       

    (r'^create/$','cv_models.sfm_3dmodel.views.create_model'),
    (r'^create/blank/$','cv_models.sfm_3dmodel.views.create_blank_model'),
    (r'^model/(?P<model_id>[0-9]+)/info/$', 'cv_models.sfm_3dmodel.views.model_info'),
    (r'^model/(?P<model_id>[0-9]+)/download/$', 'cv_models.sfm_3dmodel.views.download_model'),                                              

    (r'^model/(?P<model_id>[0-9]+)/post/inbox/$', 'cv_models.sfm_3dmodel.views.post_to_inbox'),
    (r'^model/(?P<model_id>[0-9]+)/generate/$', 'cv_models.sfm_3dmodel.views.generate'),
)                       

"""                       
    (r'^code/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.DJ_CODE_RT+'mturk/code/'}),
    (r'^frames/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/var/datasets/'}),
    (r'^video/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/var/datasets/video/'}),
    (r'^annotations/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/var/datasets/annotations/'}),
"""



