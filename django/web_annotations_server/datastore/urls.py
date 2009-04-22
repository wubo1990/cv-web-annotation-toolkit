from django.conf.urls.defaults import *

urlpatterns = patterns('',

    (r'^segmentation/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/var/datasets/segmentations/'}),

    (r'^save_segmentation/(?P<segmentation_id>[\w-]+)/', 'datastore.views.save_segmentation'),
    (r'^load_segmentation/(?P<segmentation_id>[\w-]+)/', 'datastore.views.load_segmentation'),

    (r'^register_images/(?P<dataset_name>[\w-]+)/', 'datastore.views.register_images'),

    (r'^data/(?P<dataset_name>[\w-]+)/$', 'datastore.views.show_data_items'),
    (r'^data/(?P<dataset_name>[\w-]+)/p(?P<page>[\w]+)/$', 'datastore.views.show_data_items'),

    (r'^dataitem/(?P<item_id>[\w]+)/$', 'datastore.views.show_data_item'),

    (r'^annotation/(?P<item_id>[\w]+)/$', 'datastore.views.get_annotation'),

    (r'^new_annotation/(?P<item_id>[\w]+)/(?P<annotation_type>[\w]+)/$', 'datastore.views.new_annotation'),

    (r'^dataitem/(?P<item_id>[\w]+)/a/(?P<ref_annotation_id>[\w]+)/add/(?P<new_annotation_type>[\w]+)/$', 'datastore.views.new_related_annotation'),

)
