from django.conf.urls.defaults import *
from django.conf import settings

from django.contrib import admin
admin.autodiscover()
from django.contrib.auth import views as auth_views

urlpatterns = patterns('',

    (r'^$', 'mturk.views.main'),

    (r'^code/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.DJ_CODE_RT+'mturk/code/'}),
                       
    (r'^frames/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/var/datasets/'}),
    (r'^video/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/var/datasets/video/'}),
    (r'^annotations/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/var/datasets/annotations/'}),

    (r'^mt/', include('mturk.urls')),

    (r'^RPC2$', 'rpc4django.views.serve_rpc_request'),
    (r'^datastore/', include('datastore.urls')),

    (r'^tasks/(?P<path>.*)$', 'mturk.views.dynamic_task'),

    (r'^logout/$','django.contrib.auth.views.logout'),

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
