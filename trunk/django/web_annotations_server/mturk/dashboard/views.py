# Create your views here.
from django.shortcuts import render_to_response,get_object_or_404 

from django.contrib.auth.decorators import login_required

from mturk import models_stats
from mturk.models import *
from mturk.views import get_mt_connection

@login_required
def session_dashboard(request,session_code):
    session = get_object_or_404(Session,code=session_code);	
    stats = models_stats.session_stats(session)
    return render_to_response('mturk/dashboard/session_dashboard.html', {'session':session,'stats':stats,'user':request.user})

@login_required
def session_experimental_dashboard(request,session_code):
    session = get_object_or_404(Session,code=session_code);	
    stats = models_stats.session_stats(session)
    return render_to_response('mturk/dashboard/session_experimental_dashboard.html', {'session':session,'stats':stats,'user':request.user})

@login_required
def worker_internal_dashboard(request,worker_id):
    worker,bCreated = Worker.objects.get_or_create(session=None,worker=worker_id);	
    stats = models_stats.worker_stats(worker)
    worker_contibutions=models_stats.worker_to_session_contributions(worker_id);

    return render_to_response('mturk/dashboard/worker_internal_dashboard.html', {'worker':worker,'stats':stats,'contributions':worker_contibutions,'user':request.user})

@login_required
def workers_overview_dashboard(request):
    stats = models_stats.workers_overview()
    return render_to_response('mturk/dashboard/workers_overview.html', {'stats':stats})



def worker_dashboard(request,worker_id):
    worker,bCreated = Worker.objects.get_or_create(session=None,worker=worker_id);	
    stats = models_stats.worker_stats(worker)
    worker_contibutions=models_stats.worker_to_session_contributions(worker_id);

    worker_training_info=WorkerTrainingProgress.objects.all().filter(worker=worker);

    return render_to_response('mturk/dashboard/worker_dashboard.html', {'worker':worker,'stats':stats,'contributions':worker_contibutions,'worker_training_info':worker_training_info})
