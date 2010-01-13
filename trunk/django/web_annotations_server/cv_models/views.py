# Create your views here.

import urllib,uuid,os,sys,shutil,subprocess,copy
import cPickle as pickler

from django.conf import settings
from django.core.files.storage import FileSystemStorage

from django.http import HttpResponse,Http404,HttpResponseRedirect
from django.shortcuts import render_to_response,get_object_or_404 
from django.views.generic.list_detail import object_list

from django.contrib.auth.decorators import login_required
from subprocess import *
from django.views.static import serve
import django

from models import *
import stats


def main(request):
    models=LearnedModel.objects.all();
    return render_to_response('cv_models/main.html',{'user':request.user,'models':models});    

def download_model(request,model_id,object_tag):
    model = get_object_or_404(LearnedModel,id=model_id)
    targets=model.targets.filter(target_code=object_tag);
    print targets
    if targets.count() != 1:
        raise Http404
    target = targets[0];
    if model.model_type == 1: #PF-HOG
        ext="mat"
    else:
        raise Http404
    path='%d/models/%s.%s'%(model.id,target.target_code,ext);
    print path
    return django.views.static.serve(request,document_root=settings.MODEL_STORE_ROOT,path=path);
    
    task = get_object_or_404(LearnedModel,id=model_id)
    
    return 




def model_dashboard(request,model_id):
    
    model = get_object_or_404(LearnedModel,id=model_id)
    accuracy_report = stats.get_model_performance_stats(model);
    model_progress = stats.get_model_progress_information(model);

    return render_to_response('cv_models/model_dashboard.html',{'user':request.user,'model':model,'m':model,'accuracy_report':accuracy_report,'progress':model_progress});    
