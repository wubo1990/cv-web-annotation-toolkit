from django.conf.urls.defaults import *

urlpatterns = patterns('',

    (r'^index.html', 'datastore.views.index'),

    (r'^segmentation/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/var/datasets/segmentations/'}),

    (r'^save_segmentation/(?P<segmentation_id>[\w-]+)/', 'datastore.views.save_segmentation'),
    (r'^load_segmentation/(?P<segmentation_id>[\w-]+)/', 'datastore.views.load_segmentation'),
    (r'^get_segmentation/(?P<segmentation_id>[\w-]+)/png/', 'datastore.views.get_segmentation_img'),



    (r'^register_images/(?P<dataset_name>[\w-]+)/$', 'datastore.views.register_images'),
    (r'^register_voc_boxes/(?P<dataset_name>[\w-]+)/$', 'datastore.views.register_voc_boxes'),
    (r'^register_voc_box_child_annotations/(?P<dataset_name>[\w-]+)/(?P<annotation_id>[\w]+)/$', 'datastore.views.register_voc_box_child_annotations'),
    (r'^register_voc_box_child_annotations/(?P<dataset_name>[\w-]+)/$', 'datastore.views.register_voc_box_child_annotations'),

    (r'^register_labelme_box_child_annotations/(?P<dataset_name>[\w-]+)/(?P<annotation_id>[\w]+)/$', 'datastore.views.register_labelme_box_child_annotations'),
    (r'^register_labelme_box_child_annotations/(?P<dataset_name>[\w-]+)/$', 'datastore.views.register_labelme_box_child_annotations'),
    (r'^register_labelme_boxes/(?P<dataset_name>[\w-]+)/$', 'datastore.views.register_labelme_boxes'),


    (r'^wnd/(?P<item_id>[\w.-]+)/(?P<l>[\w.-]+),(?P<t>[\w.-]+),(?P<w>[\w.-]+),(?P<h>[\w.-]+)/$', 'datastore.views.get_wnd'),


    (r'^data/(?P<dataset_name>[\w-]+)/$', 'datastore.views.show_data_items'),
    (r'^data/(?P<dataset_name>[\w-]+)/p(?P<page>[\w]+)/$', 'datastore.views.show_data_items'),

    (r'^dataitem/(?P<item_id>[\w]+)/$', 'datastore.views.show_data_item'),



    (r'^annotation/(?P<item_id>[\w]+)/$', 'datastore.views.get_annotation'),
    (r'^annotation/(?P<ref_annotation_id>[\w]+)/add/(?P<new_annotation_type>[\w]+)/$', 'datastore.views.new_related_annotation'),

    (r'^show/annotation/(?P<item_id>[\w]+)/$', 'datastore.views.show_annotation'),
    (r'^show/annotation/(?P<ref_annotation_id>[\w]+)/add/(?P<new_annotation_type>[\w]+)/$', 'datastore.views.new_related_annotation',{'depth':2,'item_id':None}),


    (r'new_annotation/(?P<item_id>[\w]+)/(?P<annotation_type>[\w]+)/$', 'datastore.views.new_annotation'),


    (r'^dataitem/(?P<item_id>[\w]+)/(?P<ref_annotation_id>[\w]+)/add/(?P<new_annotation_type>[\w]+)/$', 'datastore.views.new_related_annotation',{'depth':3}),

    (r'^.*/a/(?P<ref_annotation_id>[\w]+)/add/(?P<new_annotation_type>[\w]+)/$', 'datastore.views.new_related_annotation',{'depth':4}),

    (r'^annotation/(?P<annotation_id>[\w]+)/flag/(?P<flag>[\w]+)/$', 'datastore.views.flag_annotation'),
    (r'^annotation/(?P<annotation_id>[\w]+)/unflag/(?P<flag>[\w]+)/$', 'datastore.views.unflag_annotation'),

    (r'^show/annotated_images/(?P<dataset_name>[\w]+)/(?P<annotation_type>[\w]+)/$', 'datastore.views.show_dataset_annotations'),
    (r'^show/annotated_images/(?P<dataset_name>[\w]+)/(?P<annotation_type>[\w]+)/p(?P<page>[\w]+)/$', 'datastore.views.show_dataset_annotations'),

    (r'^show/bbox_objects/(?P<object_name>[\w]+)/p(?P<page>[\w]+)/$', 'datastore.views.show_bbox_objects'),


    (r'^show/flagged_annotations/(?P<dataset_name>[\w]+)/(?P<annotation_type>[\w]+)/(?P<flag_name>[\w]+)/p(?P<page>[\w]+)/$', 'datastore.views.show_flagged_annotations'),
    (r'^show/flagged_annotations/(?P<dataset_name>[\w]+)/(?P<flag_name>[\w]+)/p(?P<page>[\w]+)/$', 'datastore.views.show_flagged_annotations'),


    #Prefix-based URLs
    (r'^show/item_annotation/n/(?P<item_name>[\w/]+)', 'datastore.views.show_item_annotation'),



)
