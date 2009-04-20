from django.conf.urls.defaults import *

urlpatterns = patterns('',

    (r'^segmentation/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/var/datasets/segmentations/'}),

    (r'^save_segmentation/(?P<segmentation_id>[\w-]+)/', 'datastore.views.save_segmentation'),
    (r'^load_segmentation/(?P<segmentation_id>[\w-]+)/', 'datastore.views.load_segmentation'),

)
