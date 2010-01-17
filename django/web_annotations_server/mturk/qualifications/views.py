


import time

try:
    from boto.mturk.connection import MTurkConnection
    from boto.mturk.question import ExternalQuestion
    from boto.mturk.qualification import Qualifications, PercentAssignmentsApprovedRequirement,Requirement
    from boto.mturk.qualification_type import *
    hasBoto=True
except:
    hasBoto=False


from mturk.models import *

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse,Http404,HttpResponseRedirect
from django.shortcuts import render_to_response,get_object_or_404 

from django.conf import settings

from mturk.common import *

import models

"""Qualifications module. Connect internal qualification representation to Amazon's.
Supported features:
  Built-in qualifications
  Question/Answer - based qualifications
  Creation and update of qualifications
"""

@login_required
def main(request):
    return render_to_response('mturk/qualifications/main.html');










@login_required
def create_qualification(request,session_code,qualification_name):
    session = get_object_or_404(Session,code=session_code)
    qual = get_object_or_404(MTurkQualification,name=qualification_name)
    try:
        (id,created)=create_qualification_internal(session,qual)
        if created:
            return HttpResponse("+ Created qualification id:" + id);
        else:
            return HttpResponse("+ Found qualification id:" + id);
    except MTurkException, ex:
        return render_to_response('mturk/aws_error_report.html',{'resultset':ex.rs,'session':session});


@login_required
def update_qualification(request,session_code,qualification_name):
    session = get_object_or_404(Session,code=session_code)
    qual = get_object_or_404(MTurkQualification,name=qualification_name)
    try:
        if qual.mt_qual_id=="":
            (id,created)=create_qualification_internal(session,qual)
            if created:
                return HttpResponse("+ Created qualification id:" + id);
            
        update_qualification_internal(session,qual)
        
        return HttpResponse("+ Updated qualification:" + qual.mt_qual_id);

    except MTurkException, ex:
        return render_to_response('mturk/aws_error_report.html',{'resultset':ex.rs,'session':session});



@login_required
def question_xml(request,qualification_def_name):
    qual = get_object_or_404(MTurkQualificationDefinition,name=qualification_def_name)
    return HttpResponse(qual.question,mimetype="text/xml");

 

@login_required
def answer_xml(request,qualification_def_name):
    qual = get_object_or_404(MTurkQualificationDefinition,name=qualification_def_name)
    return HttpResponse(qual.answer,mimetype="text/xml");


@login_required
def create_qualifications_for_worker_metrics(request,funding_account):
    acct = get_object_or_404(FundingAccount,name=funding_account)
    try:
        create_qualifications_for_worker_metrics_internal(acct)
    except MTurkException, ex:
        return render_to_response('mturk/aws_error_report.html',{'resultset':ex.rs,'session':session});            
    return HttpResponse("+ done")

def create_qualifications_for_worker_metrics_internal(funding_account):
    for engine,is_sandbox in [(1,True),(2,False)]:
    #for engine,is_sandbox in [(1,True)]:
        conn= get_mt_connection_for_account(funding_account,is_sandbox);
        for metric in [1,2,3]:
            q,created=WorkerMetricsQualifications.objects.get_or_create(account=funding_account,engine=engine,metric_type=metric);
            params={'Name':settings.MTURK_QUALIFICATIONS_PREFIX + q.get_metric_type_display(),
                    'Description':'Automatic qualification',
                    'Keywords':'',
                    'QualificationTypeStatus':'Active'
                    };
            (id,created)=create_or_find_qualification(conn,params)
            q.external_id=id;
            q.save();

            

@login_required
def assign_qualifications_to_workers(request,funding_account):
    acct = get_object_or_404(FundingAccount,name=funding_account)
    try:
        assign_built_in_qualifications_to_workers(acct);
    except MTurkException, ex:
        return render_to_response('mturk/aws_error_report.html',{'resultset':ex.rs,'session':session});            
    return HttpResponse("+ done")


def assign_qualification(conn,q,w,qual_value):
    params={'QualificationTypeId':q.external_id,
            'WorkerId':w.worker.worker,
            'IntegerValue':str(qual_value),
            'SendNotification':'false'}
    print w.worker.worker,q.get_metric_type_display(),qual_value
    response = conn._process_request('AssignQualification', params)
    if not response.status:
        params['SubjectId']=params['WorkerId'];
        response = conn._process_request('UpdateQualificationScore', params)


def valid_worker(w,acct,is_sandbox):
    c=SubmittedTask.objects.all().filter(worker=w.worker.worker,session__funding__id=acct.id,session__sandbox=is_sandbox).count()
    print w.worker.worker,c
    return c

def assign_built_in_qualifications_to_workers(funding_account):
    acct = get_object_or_404(FundingAccount,name=funding_account)
    #for engine,is_sandbox in [(1,True),(2,False)]:
    #for engine,is_sandbox in [(1,True)]:
    for engine,is_sandbox in [(2,False)]:
        conn= get_mt_connection_for_account(acct,is_sandbox);
        q={};
        for metric in [1,2,3]:
            q[metric]=WorkerMetricsQualifications.objects.get(account=acct,engine=engine,metric_type=metric);
        
        for w in WorkerProfile.objects.all():
            if not valid_worker(w,acct,is_sandbox):
                continue
            #Worker level
            assign_qualification(conn,q[1],w,w.level);

            #Num approved
            assign_qualification(conn,q[2],w,w.num_approved);

            #GPA
            assign_qualification(conn,q[3],w,int(w.GPA*10));
            time.sleep(0.1)


@login_required
def update_internal_qualifications(request):
    try:
        models.compute_worker_statistics()
        #assign_built_in_qualifications_to_workers(acct);
    except MTurkException, ex:
        return render_to_response('mturk/aws_error_report.html',{'resultset':ex.rs,'session':session});            
    return HttpResponse("+ done")



