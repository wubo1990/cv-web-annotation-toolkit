from django.conf.urls.defaults import *
from django.conf import settings


urlpatterns = patterns('',

    (r'^$', 'cv_models.views.main'),
    (r'^download/(?P<model_id>[0-9]+)/(?P<object_tag>[\w-]+)/', 'cv_models.views.download_model'),

    (r'^model/(?P<model_id>[0-9]+)/', 'cv_models.views.model_dashboard'),

    (r'^sfm3d/', include('cv_models.sfm_3dmodel.urls')),
                       
)

"""                       
    (r'^code/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.DJ_CODE_RT+'mturk/code/'}),
    (r'^frames/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/var/datasets/'}),
    (r'^video/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/var/datasets/video/'}),
    (r'^annotations/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/var/datasets/annotations/'}),


    (r'^mt/', include('mturk.urls')),
    (r'^datastore/', include('datastore.urls')),

    #(r'^ds/', include('datasets.urls')),

    (r'^ic/', include('image_collector.urls')),

    (r'^eval/', include('evaluation.urls')),

    (r'^autograding/', include('autograding.urls')),
                       

    (r'^tasks/(?P<path>.*)$', 'mturk.views.dynamic_task'),

    (r'^people/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/var/datasets/people/'}),
)
"""
