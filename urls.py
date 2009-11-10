from django.conf.urls.defaults import *
from django.conf import settings

from django.contrib import admin
admin.autodiscover()
from django.contrib.auth import views as auth_views

urlpatterns = patterns('',

    (r'^$', 'evaluation.views.main'),

                       
    (r'^code/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.DJ_CODE_RT+'mturk/code/'}),
    (r'^frames/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/var/datasets/'}),
    (r'^annotations/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/var/datasets/annotations/'}),


    (r'^mt/', include('mturk.urls')),
    (r'^datastore/', include('datastore.urls')),

    #(r'^ds/', include('datasets.urls')),

    (r'^ic/', include('image_collector.urls')),

    (r'^eval/', include('evaluation.urls')),
                       

    (r'^tasks/(?P<path>.*)$', 'mturk.views.dynamic_task'),

    (r'^people/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/var/datasets/people/'}),

    (r'^sense/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/var/datasets/sense_annotation/'}),

#    ('^([^/]+)/([^/]+)/(.+)/$', 'django.contrib.admin.views.main.change_stage'),

    ('^admin/mturk/session/add/$', 'mturk.adminview.add_session'),
    ('^admin/mturk/session/(\d+)/$', 'mturk.adminview.edit_session'),
    ('^admin/mturk/session/(\d+)/delete/$', 'mturk.adminview.delete_session'),
    ('^admin/mturk/task/(\d+)/$', 'mturk.adminview.edit_task'),
    ('^admin/mturk/task/(\d+)/delete/$', 'mturk.adminview.delete_task'),




    (r'^logout/$','django.contrib.auth.views.logout'),
    #(r'^accounts/login/$', 'django.contrib.auth.views.login'),

    #This is a local modification of the registration app 


    (r'^accounts/', include('evaluation.registration_urls')),
    (r'^accounts/profile/$', 'django.views.generic.simple.redirect_to',{'url':'/'}),
                       
    url(r'^accounts/password/logout/$',
                           auth_views.logout,
                           {'template_name': 'registration/logout.html'},
                           name='auth_logout'),

    # Uncomment this for admin:
    (r'^admin/(.*)', admin.site.root)


)
