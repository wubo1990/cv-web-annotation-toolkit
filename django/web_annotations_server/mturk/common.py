
""" All functions directly connected to MTurk communication """

from django.conf import settings

if settings.MTURK_INTEGRATION:
    from boto.mturk.connection import MTurkConnection
    from boto.mturk.question import ExternalQuestion
    from boto.mturk.qualification import Qualifications, PercentAssignmentsApprovedRequirement,Requirement
    from boto.mturk.qualification_type import *
    import qualifications.views as qual_views
    hasBoto=True
else:
    print "MTURK integration is disabled. This application will be pretty useless."
    hasBoto=False

from mturk.models import *

class MTurkException(Exception):
     def __init__(self, rs):
         self.rs = rs
     def __str__(self):
         return str(self.rs)


def get_mt_connection(session):
    if session.sandbox:
        awshost='mechanicalturk.sandbox.amazonaws.com'
    else:
        awshost='mechanicalturk.amazonaws.com'

    conn = MTurkConnection(host=awshost,
                           aws_secret_access_key=session.funding.secret_key.encode('ascii'),
                           aws_access_key_id=session.funding.access_key.encode('ascii'))

    return conn


def get_mt_connection_for_account(funding,is_sandbox):
    if is_sandbox:
        awshost='mechanicalturk.sandbox.amazonaws.com'
    else:
        awshost='mechanicalturk.amazonaws.com'

    conn = MTurkConnection(host=awshost,
                           aws_secret_access_key=session.funding.secret_key.encode('ascii'),
                           aws_access_key_id=session.funding.access_key.encode('ascii'))
    return conn





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


def add_session_qualifications(qualifications,session):
    """Add all qualifications relevant to a session. Create the qualifications as necessary."""

    qualifications.add(PercentAssignmentsApprovedRequirement(comparator="GreaterThan", integer_value="90"))
    force_create=False
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




def create_or_find_qualification(conn,params):
    """Try to create the qualification. If it fails, try to find it. In all fails, raise an exception"""

    response = conn.make_request('CreateQualificationType', params,verb='POST')
    resp= conn._process_response(response, [('CreateQualificationTypeResponse',QualificationType)])
    if resp.status != True:
        raise MTurkException(resp)

    resp_qual=resp[0]
    if resp_qual.valid:
        id = resp_qual.id
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
            if q.name==qual_name:
                id=q.id
                created=False
                return (id,created)

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




def activate_hit(session,hit):
    if session.standalone_mode:
        return (True,"%s" % hit.ext_hitid)

    taskurl=settings.HOST_NAME_FOR_MTURK+"mt/get_task/"+str(session.code)+"/?extid="+hit.ext_hitid;

    q = ExternalQuestion(external_url=taskurl, frame_height=800)

    conn = get_mt_connection(session)


    keywords=session.task_def.get_keywords()

    t=session.task_def;
    if not session.hit_type:
        qualifications = Qualifications()
        add_session_qualifications(qualifications,session);

        create_hit_rs = conn.create_hit(question=q, 
                                        lifetime=t.lifetime,
                                        max_assignments=t.max_assignments,
                                        title=t.title,
                                        keywords=str(t.keywords),
                                        reward = t.reward,
                                        duration=t.duration,
                                        approval_delay=t.approval_delay, 
                                        annotation="IGNORE",
                                        qualifications=qualifications)
        if create_hit_rs.status != True:
            return (False, "Error talking to AWS: %s (%s)" % (create_hit_rs.Message,create_hit_rs.Code));
        
        try:
            session.hit_type=create_hit_rs.HITTypeId;
        except Exception,e:
            print str(e)
            print str(create_hit_rs)
            return (False, "Exception found while creating HIT: %s (AWS error): %s (%s)" % (str(e),create_hit_rs.Message,create_hit_rs.Code));

        session.save();
    else:
        num_active_assignments=hit.submittedtask_set.filter(state__in=SUBMISSION_STATE_CAN_BE_VALID).count()
        num_assignments_to_activate=t.max_assignments - num_active_assignments;
        if num_assignments_to_activate<=0:
            return (True,"+ %s" %hit.ext_hitid)

        create_hit_rs = conn.create_hit(question=q, hit_type=session.hit_type, max_assignments=num_assignments_to_activate)
        

    try:
        mt_hit_id=create_hit_rs.HITId
    except:
        return (False, "Error talking to AWS: %s (%s)" % (create_hit_rs.Message,create_hit_rs.Code));
    else:
        mthit=MechTurkHit(session=session,mthit=hit,state=1,mechturk_hit_id=mt_hit_id);
        mthit.save();

        hit.state=6 #Active.
        hit.save();

        return (True,"%s" % hit.ext_hitid)



def add_hit_assignments(session,hit,num_assignments):
    if session.standalone_mode:
        return (True,"%s" % hit.ext_hitid)

    conn = get_mt_connection(session)

    mthit=MechTurkHit.objects.filter(session=session,mthit=hit)[0];
    hit_id=mthit.mechturk_hit_id;
    conn.extend_hit(hit_id,num_assignments);
    mthit.state=1;
    mthit.save();
    hit.state=6 #Active.
    hit.save();

    return (True,"%s" % hit.ext_hitid)



def expire_hit(conn,hit_id):
    params = {'HITId' : hit_id,}
    
    return conn._process_request('ForceExpireHIT', params)

def change_hit_type(conn,hit_id,hit_type_id):
    params = {'HITId' : str(hit_id),'HITTypeId':str(hit_type_id),'Operation':'ChangeHITTypeOfHIT'}
    print params
    rs =  conn._process_request('ChangeHITTypeOfHIT', params)
    #rs =  conn.temp_make_request('ChangeHITTypeOfHIT', params)
    #print rs.read()
    return rs



def mt_approve_submission(r,grade,feedback,  conn,te):
    try:
        resp = conn.approve_assignment(r.assignment_id,feedback)
        if r.valid and grade<10:
            r.valid=False;
            r.state=3
            r.save()
            te.on_deactivate(r);
        
        
        r.final_grade=str(grade);
        r.state=3;
        r.save();
        if grade<10:
            r.hit.state=5; # Open
        else:
            r.hit.state=4; # Finalized
        r.hit.save();

        return True
    except Exception,e:
        print 'Approve FAILED: %s\t"%s" : %s <br/>'% (r.assignment_id,feedback,str(e))
        return False

def mt_reject_submission(r,grade,feedback,  conn,te):
    try:
        resp = conn.reject_assignment(r.assignment_id,feedback)
        r.valid=False;
        r.state=4;
        r.final_grade=str(grade);
        r.save()
        te.on_deactivate(r);

        r.hit.state=5; # Open
        r.hit.save();
        return True
    except Exception,e:
        print 'Reject FAILED: %s\t"%s" : %s <br/>'% (r.assignment_id,feedback,str(e))
        return False




def create_session_hit_type(session):

    conn = get_mt_connection(session)

    keywords=session.task_def.get_keywords()

    t=session.task_def;
    qualifications = Qualifications()
    add_session_qualifications(qualifications,session);
    #qualifications.add(PercentAssignmentsApprovedRequirement(comparator="GreaterThan", integer_value="80"))
    print qualifications
    create_hit_rs = conn.register_hit_type(  title=t.title,
                                             description=t.description,
                                            keywords=str(t.keywords),
                                            reward = t.reward,
                                            duration=t.duration,
                                            approval_delay=t.approval_delay, 
                                            qual_req=qualifications)
    print str(create_hit_rs)
    if (create_hit_rs.status != True):
        raise MTurkException(create_hit_rs);


    print "Created HIT Type",create_hit_rs.HITTypeId
    hit_type_id=create_hit_rs.HITTypeId;
    return hit_type_id

