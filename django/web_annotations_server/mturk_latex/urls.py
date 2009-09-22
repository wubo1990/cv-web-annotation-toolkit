# Create your views here.


from django.conf.urls.defaults import *

import views

urlpatterns = patterns('',

    (r'^$', 'mturk_latex.views.main'),

    (r'^compile/$', 'mturk_latex.views.compile'),

    (r'^img/(?P<id>[\w\-]+)/$', 'mturk_latex.views.getimg'),                       


)
