
from __future__ import with_statement
import copy
import uuid

import mturk.models
from mturk.models import *
from common import *

from rpc4django import rpcmethod



def format_session(session):
    qualifications=[]
    for q in session.mturk_qualification.all():
        qualifications.append(q.name);

    session_dict = {'id':session.code,
                    'task':session.task_def.name,
                    'hit_limit':session.HITlimit,
                    'owner':session.owner.username,
                    'funding':session.funding.name,
                    'qualifications':qualifications
                    }
    if session.standalone_mode:
        session_dict['work_engine']='Internal';
    elif session.sandbox:
        session_dict['work_engine']='MT_sandbox';
    else:
        session_dict['work_engine']='MT_production';

    return session_dict;


work_unit_state_map =  {1:'Idle',     # 'New'
                        2:'Submitted', # 'Submitted'
                        3:'Reviewed', # 'Graded'
                        4:'Finalized',# Finalized
                        5:'Idle',     #, 'Open'),
                        6:'Active',   #, 'Active'),
                        7:'Idle'}     #, 'Rejected'),

def get_work_unit_state(work_unit):
    work_unit_state = work_unit_state_map[work_unit.state];
    if work_unit_state=='Active':
        num_valid_submissions=0;
        num_new_submissions=0;
        num_graded_submissions=0;
        num_good_submissions=0;
        for s in work_unit.submittedtask_set().filter(valid=True):
            num_valid_submissions += 1;
            if s.state==1: #New
                num_new_submissions +=1;
            elif s.state==2: #Graded
                num_graded_submissions +=1;
            elif s.state==3:
                num_good_submissions +=1;
        if num_good_submissions == work_unit.session.task_def.max_assignments:
            work_unit_state = 'Finalized';
    return work_unit_state

def format_work_unit(work_unit):
    work_unit_state=get_work_unit_state(work_unit);

    submission_ids=[];
    for s in work_unit.submittedtask_set.all():
        submission_ids.append(s.id);
        
    wu_dict={'id':work_unit.ext_hitid,
             'session':work_unit.session.code,
             'state':work_unit_state,
             'assignments':[],
             'submissions':submission_ids,
             'data':work_unit.parameters};

    return wu_dict;


def format_submission(submission):
    submission_dict= {'id':submission.id,
                      'session':submission.session.code,
                      'work_unit':submission.hit.ext_hitid,
                      'worker':submission.worker,
                      'data':submission.get_xml_str()};

    (start_time,end_time)=submission.get_timing();
    if start_time!='':
        submission_dict['start_time']=start_time
        submission_dict['end_time']=end_time

    grades=[]
    for g in submission.manualgraderecord_set.filter(valid=1):
        grades.append(format_grade(g));

    submission_dict['grades']=grades;

    return submission_dict

def format_grade(grade):
    grade_dict= {'id':grade.id,    
                 'quality':grade.quality,
                 'feedback':grade.feedback,
                 'worker':grade.worker,
                 'reference':grade.reference}
    return grade_dict


#permission='rpc-access')
@rpcmethod(name='mt.list_sessions',permission='mturk.add_session')
def list_sessions(**kwargs):
    request=kwargs['request'];
    print request
    sessions=[];

    print request.user
    for s in Session.objects.filter(owner=request.user):
        sessions.append(s.code)
    
    return sessions

@rpcmethod(name='mt.list_session_work_units')
def list_session_work_units(session_id):
    session=Session.objects.get(code=session_id);
    work_units=[];
    for w in session.mthit_set.all():
        work_units.append(w.ext_hitid);
    
    return work_units


@rpcmethod(name='mt.list_work_unit_submissions')
def list_work_unit_submissions(work_unit_extid):
    wu=WorkUnit.objects.get(ext_hitid=work_unit_extid);

    submissions=[];
    for s in wu.submittedtask_set.all():
        submissions.append(s.id);
    
    return submissions



@rpcmethod(name='mt.get_session')
def get_session(session_id):
    session=Session.objects.get(code=session_id);
    
    return format_session(session)


@rpcmethod(name='mt.get_session_work_units')
def get_session_work_units(session_id):
    session=Session.objects.get(code=session_id);
    work_units=[];
    for w in session.mthit_set.all():
        work_units.append(format_work_unit(w));
    
    return work_units



@rpcmethod(name='mt.get_work_unit_submissions')
def get_work_unit_submissions(work_unit_extid):
    wu=WorkUnit.objects.get(ext_hitid=work_unit_extid);

    submissions=[];
    for s in wu.submittedtask_set.all():
        submissions.append(format_submission(s));
    
    return submissions



def get_submission_grade_optimistic(st):
    grade=None
    feedback="";
    for g in st.manualgraderecord_set.filter(valid=True):
        if grade:
            if grade>g.quality:
                grade=g.quality;
                feedback=g.feedback;
            else:
                grade=g.quality;
                feedback=g.feedback;

    return (grade,feedback)




@rpcmethod(name='mt.get_work_unit_submissions_filtered')
def get_work_unit_submissions_filtered(work_unit_extid,filter):
    wu=WorkUnit.objects.get(ext_hitid=work_unit_extid);

    submissions=[];
    for s in wu.submittedtask_set.all():
        (grade,feedback) = get_submission_grade_optimistic(s)
        if grade is not None and grade>7:
            submissions.append(format_submission(s));
    
    return submissions






@rpcmethod(name='mt.create_session', permission='mturk.add_session')
def create_session(code,task_id,crowd_engine,funding,work_unit_limit,qualifications,**kwargs):
    task=get_object_or_404(Task,name=task_id);
    funding=get_object_or_404(FundingAccount,name=funding);
    if crowd_engine=='Internal':
        is_standalone=True
        is_sandbox=True; #just in case
    elif crowd_engine=='MT_sandbox':
        is_standalone=False
        is_sandbox=True
    elif crowd_engine=='MT_production':
        is_standalone=False
        is_sandbox=True

    request=kwargs['request'];
    owner=request.user;

    s=mturk.models.Session(code=code,task_def=task,funding=funding,standalone_mode=is_standalone, sandbox=is_sandbox,HITlimit=work_unit_limit,owner=owner)
    s.save()
    return str(s.code)


@rpcmethod(name='mt.copy_session', permission='mturk.add_session')
def copy_session(prototype_session_code,new_session_code,**kwargs):
    session = get_object_or_404(Session,code=prototype_session_code);
    try:
        new_session = Session.objects.get(code=new_session_code)
        return 'Error: session exists'
    except:
        pass

    new_session=copy.copy(session);
    new_session.code=new_session_code;
    new_session.id = None;
    new_session.save();
    for q in session.mturk_qualification.all():
        new_session.mturk_qualification.add(q)
    return str(new_session.id)


@rpcmethod(name='mt.create_work_unit', permission='mturk.add_mthit')
def create_work_unit(session_id,parameters,shall_activate,**kwargs):
    session=get_object_or_404(Session,code=session_id)

    if session.mthit_set.count()>=session.HITlimit:
        return "Error: HIT creation failed: maximum HIT count (%d) reached" % session.HITlimit

    id = session.mthit_set.count()+1;

    rand_id=str(uuid.uuid4())+"-"+str(id)

    hit=MTHit(session=session,ext_hitid=rand_id,int_hitid=id,parameters=parameters);
    hit.save();

    if not session.standalone_mode and shall_activate:
        created,ext_id = activate_hit(session,hit)
    else:
        ext_id = hit.ext_hitid

    return ext_id


def generate_image_id(self,prefix=None):
    rand_id=str(uuid.uuid4())
    if prefix:
        return prefix+"-"+rand_id
    else:
        return rand_id

@rpcmethod(name='mt.post_image')
def post_image(session_id,img,image_name,reduce_jpeg_resolution=None,web_jpeg_quality=None,**kwargs):
    session=get_object_or_404(Session,code=session_id)

    if image_name is None or image_name=='' or image_name=='*AUTO':
        image_name=generate_image_id()+".jpg"
    
    image_dir=os.path.join(settings.DATASETS_ROOT,session.code);
    if not os.path.exists(image_dir):
        os.makedirs(image_dir);
    image_file_name=os.path.join(image_dir,image_name)
    with open(image_file_name,'wb') as image_file:
        image_file.write(img.data);


    return image_name



@rpcmethod(name='mt.submit_work',permission='mturk.can_submit_work') #This is weaker than "add_submission"
def submit_work(work_unit_id,worker,assignment_id,data,**kwargs):
    work_unit=get_object_or_404(WorkUnit,ext_hitid=work_unit_id);

    session=work_unit.session;

    GET={};
    POST=data;
    postS=pickler.dumps((GET,POST));
    submission=SubmittedTask(hit=work_unit,session_id=session.id,worker=worker,assignment_id=assignment_id, response=postS);
    submission.save();
    session.task_def.type.get_engine().on_submit(submission);

    work_unit.state=2; #Submitted
    work_unit.save();

    return submission.id;



@rpcmethod(name='mt.submit_grade',permission='mturk.add_manualgraderecord')
def submit_grade(submission_id,worker,assignment_id,data,**kwargs):
    request=kwargs['request'];

    submission = get_object_or_404(SubmittedTask,id=submission_id)


    (worker,created)=Worker.objects.get_or_create(worker=request.user.username)
    if created and request.user.is_superuser:
        worker.utility = 100;
        worker.save()


    gr=ManualGradeRecord(submission=submission,quality=int(quality),feedback=feedback,worker=worker)
    gr.save();

    return True
