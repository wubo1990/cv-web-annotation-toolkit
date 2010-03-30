from django.conf.urls.defaults import *
from django.conf import settings

from django.contrib import admin
admin.autodiscover()
from django.contrib.auth import views as auth_views

urlpatterns = patterns('',

    #(r'^$', 'web_menu.views.start'),
    (r'^$', 'mturk.views.main'),
    (r'^code/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.DJ_CODE_RT+'mturk/code/'}),
                       
    (r'^code/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.DJ_CODE_RT+'mturk/code/'}),
    (r'^frames/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/var/datasets/'}),
    (r'^video/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/var/datasets/video/'}),
    (r'^annotations/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/var/datasets/annotations/'}),


    (r'^mt/', include('mturk.urls')),

    (r'^RPC2$', 'rpc4django.views.serve_rpc_request'),
    (r'^datastore/', include('datastore.urls')),

    #(r'^ds/', include('datasets.urls')),

    (r'^ic/', include('image_collector.urls')),

    (r'^eval/', include('evaluation.urls')),

    (r'^autograding/', include('autograding.urls')),
                       
    (r'^web_menu/', include('web_menu.urls')),

    (r'^tasks/(?P<path>.*)$', 'mturk.views.dynamic_task'),

    (r'^people/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/var/datasets/people/'}),

    (r'^sense/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/var/datasets/sense_annotation/'}),

    (r'^mt_latex/', include('mturk_latex.urls')),
#    ('^([^/]+)/([^/]+)/(.+)/$', 'django.contrib.admin.views.main.change_stage'),

    (r'^cv_models/', include('cv_models.urls')),

#    These functions should work, but they don't #
#
#    ('^admin/mturk/session/add/$', 'mturk.adminview.add_session'),
#    ('^admin/mturk/session/(\d+)/$', 'mturk.adminview.edit_session'),
#    ('^admin/mturk/session/(\d+)/delete/$', 'mturk.adminview.delete_session'),
#    ('^admin/mturk/task/(\d+)/$', 'mturk.adminview.edit_task'),
#    ('^admin/mturk/task/(\d+)/delete/$', 'mturk.adminview.delete_task'),




    (r'^logout/$','django.contrib.auth.views.logout'),
    #(r'^accounts/login/$', 'django.contrib.auth.views.login'),

    #This is a local modification of the registration app 
    (r'^accounts/', include('registration.urls')),
    (r'^accounts/profile/$', 'django.views.generic.simple.redirect_to',{'url':'/'}),
                       
    url(r'^accounts/password/logout/$',
                           auth_views.logout,
                           {'template_name': 'registration/logout.html'},
                           name='auth_logout'),

    # Uncomment this for admin:
    (r'^admin/', include(admin.site.urls))


)
