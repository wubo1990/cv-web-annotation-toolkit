# Create your views here.

import urllib,uuid,os,sys,shutil,subprocess
import cPickle as pickler

from django.conf import settings

from django.http import HttpResponse,Http404,HttpResponseRedirect
from django.shortcuts import render_to_response,get_object_or_404 
from django.views.generic.list_detail import object_list
from django.contrib.auth.decorators import login_required


from models import *
import models_stats

#from annotation.datasets.views import get_frames_list_internal

#import mturk.protocols.people14.views as people14_views







@login_required
def session_stats_by_worker(request,session_code):
    session = get_object_or_404(Session,code=session_code)
    
    session_stats= models_stats.worker_contributions_to_session(session);

    return render_to_response('mturk/session_stats__by_worker.html',
                              {'session':session,'session_stats':session_stats});








