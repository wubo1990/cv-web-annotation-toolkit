

try:
    from boto.mturk.connection import MTurkConnection
    from boto.mturk.question import ExternalQuestion
    from boto.mturk.qualification import Qualifications, PercentAssignmentsApprovedRequirement,Requirement
    from boto.mturk.qualification_type import *
    import qualifications.views as qual_views
    hasBoto=True
except:
    hasBoto=False


from mturk.models import *


def add_session_qualifications(qualifications,session,force_create=False):
    qualifications.add(PercentAssignmentsApprovedRequirement(comparator="GreaterThan", integer_value="90"))

    for q in session.mturk_qualification.all():
        print "QUAL",q.id
        if q.mt_qual_id is None or q.mt_qual_id =="" or force_create:
            create_qualification_internal(session,q)

        req=Requirement(
                qualification_type_id=q.mt_qual_id,
                comparator=q.comparator,
                integer_value=q.value, 
                required_to_preview=False);
        qualifications.add(req);
    return qualifications



def create_qualification_internal(session,qual):

    qual_definition = qual.qualification_def; 
    params={'Name':qual_definition.name,
            'Description':'',
            'Keywords':''};
    for prop in qual_definition.properties.split('\n'):
        print prop
        if prop.strip()=="":
            continue
        (k,v)=prop.split('=');
        params[k]=v.strip()
        
    params['Test']=qual_definition.question
    params['AnswerKey']=qual_definition.answer
    params['QualificationTypeStatus']='Active'

    print params
    conn = get_mt_connection(session);

    response = conn.make_request('CreateQualificationType', params,verb='POST')
    print response.status
    resp= conn._process_response(response, [('CreateQualificationTypeResponse',QualificationType)])
    print resp,response
    #resp=conn._process_request('CreateQualificationType',params);
    print resp
    if resp.status != True:
        print resp
        raise MTurkException(resp)

    resp_qual=resp[0]
    if resp_qual.valid:
        id = resp_qual.id
        qual.mt_qual_id=id
        qual.save()
    else:
        id= None

    return id



@login_required
def create_qualification(request,session_code,qualification_name):
    session = get_object_or_404(Session,code=session_code)
    qual = get_object_or_404(MTurkQualification,name=qualification_name)
    try:
        create_qualification_internal(session,qual)
        return HttpResponse("+");
    except MTurkException, ex:
        return render_to_response('mturk/aws_error_report.html',{'resultset':ex.rs,'session':session});

