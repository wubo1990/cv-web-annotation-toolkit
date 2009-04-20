from django.conf.urls.defaults import *
from django.conf import settings

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',

    (r'^code/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.DJ_CODE_RT+'mturk/code/'}),
    (r'^frames/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/var/datasets/'}),
    (r'^annotations/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/var/datasets/annotations/'}),


    (r'^mt/', include('mturk.urls')),
    (r'^datastore/', include('datastore.urls')),

    #(r'^ds/', include('datasets.urls')),

    (r'^ic/', include('image_collector.urls')),



    (r'^tasks/(?P<path>.*)$', 'mturk.views.dynamic_task'),

    (r'^people/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/var/datasets/people/'}),

    (r'^sense/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/var/datasets/sense_annotation/'}),

#    ('^([^/]+)/([^/]+)/(.+)/$', 'django.contrib.admin.views.main.change_stage'),

    ('^admin/mturk/session/add/$', 'mturk.adminview.add_session'),
    ('^admin/mturk/session/(\d+)/$', 'mturk.adminview.edit_session'),
    ('^admin/mturk/session/(\d+)/delete/$', 'mturk.adminview.delete_session'),
    ('^admin/mturk/task/(\d+)/$', 'mturk.adminview.edit_task'),
    ('^admin/mturk/task/(\d+)/delete/$', 'mturk.adminview.delete_task'),



    # Uncomment this for admin:
    (r'^admin/(.*)', admin.site.root)


)
