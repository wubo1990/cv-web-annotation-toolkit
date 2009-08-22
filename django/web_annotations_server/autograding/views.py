# Create your views here.

import os, shutil
from django.conf import settings
from django.shortcuts import render_to_response,get_object_or_404 
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse,Http404,HttpResponseRedirect
from mturk.models import *

import create_flat_file
import build_te_model
import round_predictions

AUTOGRADING_MODEL_ROOT=os.path.join(settings.DATASETS_ROOT,'autograding_models')



def main(request):
    models=[]
    for t in Task.objects.all():
        ag_model_fn = os.path.join(AUTOGRADING_MODEL_ROOT, t.name, 'ag_grading.bin');
        if os.path.exists(ag_model_fn):
            models.append((t.name,ag_model_fn));
    return render_to_response('autograding/main.html',{'user':request.user,'models':models});

@login_required
def grade_session_with_automatic_model(request,session_code):
    session = get_object_or_404(Session,code=session_code)
    task_name = session.task_def.name;
    ag_model_fn = os.path.join(AUTOGRADING_MODEL_ROOT, task_name, 'ag_grading.bin');
    if not os.path.exists(ag_model_fn):
        return HttpResponse("No model."+ag_model_fn)
    
    temp_root=os.path.join('/var/tmp/autograding',session_code)
    if not os.path.exists(temp_root):
        os.makedirs(temp_root)
    
    create_flat_file.create_grading_flat_file(session.code,temp_root, [0,0,1])

    build_te_model.make_predictions_with_model(temp_root,ag_model_fn)
    (predictions,gt_url) = round_predictions.round_predictions(temp_root)

    (wrk,is_created)=Worker.objects.get_or_create(worker="AUTO-ADDITIVE-GROVES");

    resp=HttpResponse("Done.")
    for pred, ref in map(None,predictions,gt_url):
        submission_id = int(ref.split('\t')[0])
        resp.write("%d\t%d\n" % (submission_id,pred))
        subm = get_object_or_404(SubmittedTask,id=submission_id)
        (rcd,created)=ManualGradeRecord.objects.get_or_create(submission=subm,
                                                              worker=wrk);
        rcd.feedback="Computer-generated grade"
        rcd.quality=pred;
        rcd.save();

    return resp


@login_required
def build_model_from_session(request,session_code):
    session = get_object_or_404(Session,code=session_code)
    task_name = session.task_def.name;

    ag_model_fn = os.path.join(AUTOGRADING_MODEL_ROOT, task_name, 'ag_grading.bin');

    ag_training_root = os.path.join(AUTOGRADING_MODEL_ROOT, task_name, 'training');
    if not os.path.exists(ag_training_root):
        #os.rmdir(ag_training_root);
        os.makedirs(ag_training_root);

    temp_root=os.path.join('/var/tmp/autograding',session_code)
    if not os.path.exists(temp_root):
        os.makedirs(temp_root)

    resp=HttpResponse("Building grading model:\n",mimetype="text/plain")    
    resp.write("Creating data file\n")
    resp.flush()
    create_flat_file.create_grading_flat_file(session.code, ag_training_root, [0.5,0.25,0.25])
    resp.write(" done\n")


    resp.write("Learning the model on train+val\n")
    resp.flush()
    build_te_model.build_model(ag_training_root);
    resp.write(" done\n")

    ag_trained_model_fn=os.path.join(ag_training_root,'model.bin')
    build_te_model.make_predictions_with_model(ag_training_root,ag_trained_model_fn)

    resp.write("Predicting on the testset\n")
    resp.flush()
    round_predictions.round_predictions(ag_training_root)
    resp.write(" done\n")
    resp.write("----------------\n")
    resp.write("Testset report\n")
    rpt_fn=os.path.join(ag_training_root,'preds.txt.report.txt')
    for s in open(rpt_fn,'r').readlines():
        resp.write(s)
    
    shutil.copyfile(ag_trained_model_fn,ag_model_fn)
    return resp


@login_required
def deactivate_autmatic_grades(request,session_code):
    session = get_object_or_404(Session,code=session_code)
    rcd_set=ManualGradeRecord.objects.filter(submission__session__code=session.code,worker__worker__startswith='AUTO-');
    nDeactivated=0;
    for m in rcd_set:
        m.valid=False
        m.save();
        nDeactivated +=1
    return HttpResponse("Deactivated %d grades." % nDeactivated)

@login_required
def activate_autmatic_grades(request,session_code):
    session = get_object_or_404(Session,code=session_code)
    rcd_set=ManualGradeRecord.objects.filter(submission__session__code=session.code,worker__worker__startswith='AUTO-');
    nActivated=0;
    for m in rcd_set:
        m.valid=True
        m.save();
        nActivated +=1
    return HttpResponse("Activated %d grades." % nActivated)

