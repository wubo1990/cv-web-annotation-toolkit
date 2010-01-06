




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

from mturk.common import *

"""Qualifications module. Connect internal qualification representation to Amazon's.
Supported features:
  Built-in qualifications
  Question/Answer - based qualifications
  Creation and update of qualifications
"""

def add_session_qualifications(qualifications,session):
    """Add all qualifications relevant to a session. Create the qualifications as necessary."""

    qualifications.add(PercentAssignmentsApprovedRequirement(comparator="GreaterThan", integer_value="90"))

    for q in session.mturk_qualification.all():
        if q.mt_qual_id is None or q.mt_qual_id =="" or force_create:
            create_qualification_internal(session,q)

        req=Requirement(
                qualification_type_id=q.mt_qual_id,
                comparator=q.comparator,
                integer_value=q.value, 
                required_to_preview=False);
        qualifications.add(req);
    return qualifications



def get_qualification_parameters(qual):
    """Get the parameters dictionary to create the qualification. Use internal parameters and parse qual_definition.properties."""

    qual_definition = qual.qualification_def; 
    
    params={'Name':qual_definition.name,
            'Description':'',
            'Keywords':''};

    for prop in qual_definition.properties.split('\n'):
        if prop.strip()=="":
            continue
        (k,v)=prop.split('=');
        params[k]=v.strip()
        
    params['Test']=qual_definition.question
    params['AnswerKey']=qual_definition.answer
    params['QualificationTypeStatus']='Active'

    return params

def create_qualification_internal(session,qual):
    """Try to create the qualification. If it fails, try to find it. In all fails, raise an exception"""

    params=get_qualification_parameters(qual)
    conn = get_mt_connection(session);

    response = conn.make_request('CreateQualificationType', params,verb='POST')
    resp= conn._process_response(response, [('CreateQualificationTypeResponse',QualificationType)])
    if resp.status != True:
        raise MTurkException(resp)

    resp_qual=resp[0]
    if resp_qual.valid:
        id = resp_qual.id
        qual.mt_qual_id=id
        qual.save()
        created=True
        return (id,created)
    else:
        "Try to find one"
        qual_name = params["Name"];
        search_params={'Query':qual_name,'MustBeOwnedByCaller':'true','MustBeRequestable':'true'}
        search_params['PageSize']=90;
        response = conn.make_request('SearchQualificationTypes', search_params,verb='POST')
        resp= conn._process_response(response, [('QualificationType',QualificationType)])
        for q in resp:
            print q.name
            if q.name==qual_name:
                qual.mt_qual_id=q.id
                qual.save()
                created=False
                return (q.id,created)

        #Can't create and can't find - give up!
        raise MTurkException(resp_qual)


def update_qualification_internal(session,qual):
    """Update the qualification. We assume to have mt_qual_id set."""

    params=get_qualification_parameters(qual)
    params["QualificationTypeId"]=qual.mt_qual_id;
    conn = get_mt_connection(session);

    response = conn.make_request('UpdateQualificationType', params,verb='POST')
    resp= conn._process_response(response, [('QualificationType',QualificationType)])
    if resp.status != True:
        raise MTurkException(resp)

    resp_qual=resp[0]
    if not resp_qual.valid:
        raise MTurkException(resp_qual)

    return True



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



