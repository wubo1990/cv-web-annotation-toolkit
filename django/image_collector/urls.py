from django.conf.urls.defaults import *

import views

urlpatterns = patterns('',

    (r'^index/$', views.index),

    (r'^search/$', views.search_images),

    (r'^run_search/$', views.run_search),
    (r'^mark_image/(?P<source>\w+)/(?P<src_imgid>\w+)/(?P<mark>OFF|ON)/', views.mark_image),

    (r'^list_relevant/', views.list_relevant),
    (r'^full_info/(?P<source>\w+)/(?P<src_imgid>\w+)/', views.get_full_image_info),

    (r'^full_info/LICENSE_README.txt','django.views.generic.simple.direct_to_template', {'template': 'image_collector/LICENSE_README.txt'}),

    (r'^stats/',views.show_stats),

)
