

"""RPC (XML/JSON) API for the django_crowd server.

All objects are represented in JSON (i.e. via dictionary of fields)

Session representation:
   id             - Session ID  (string)
   task           - Task definition name  (string)
   hit_limit      - Maximum number of work units  (number)
   owner          - User name of the session owner (string)
   funding        - The name of the funding account  (string)
   qualifications - The list of qualification names  (list of strings)
   work_engine    - The name of the processing engine  ('Internal','MT_production','MT_sandbox')


Work unit states:
  'Idle'        - can be submitted to the processing system
  'Active'      - has been submitted to the processing system (somebody could be working on it)
  'Submitted'   - the processing system returned it to us
  'Reviewed'    - We have reviewed it 
  'Finalized'   - Done. 

Work Unit data structure:
   id           - Unique ID
   session      - The session ID
   state        - State as defined above
   assignments  - reserved
   submissions  - submission IDs
   data         - raw work unit parameters

Submission data structure:
   id           - Unique submission ID
   session      - Session ID 
   work_unit    - Work unit ID
   worker       - Worker ID
   data         - Raw submission data
   start_time   - When the work started
   end_time     - When the work ended
   grades       - List of grades (inline structures,  not IDs)

Grade data structure:
   id           - Unique grade ID
   quality      - Quality number (10 - good, 7 - approve/redo, 3 -reject)
   feedback     - (ptional) feedback
   worker       - The grader
   reference    - Grading reference (e.g. source algorithm or system tags)

"""


from __future__ import with_statement
import copy
import uuid

import mturk.models 
from mturk.common import *

print mturk.models.task_engines

from rpc4django import rpcmethod

from formatting import *

from mturk import ros_integration

#permission='rpc-access')
@rpcmethod(name='mt.list_sessions',permission='mturk.add_session')
def list_sessions(**kwargs):
    """Returns a list of sessions owned by the authenticated user . """

    request=kwargs['request'];
    print request
    sessions=[];

    print request.user
    for s in mturk.models.Session.objects.filter(owner=request.user):
        sessions.append(s.code)
    
    return sessions

@rpcmethod(name='mt.list_session_work_units')
def list_session_work_units(session_id):
    """Lists all work units in the session. Only work unit IDs are returned.
    @param  session_id: The unique session code.
    @return: [work_unit_id] The list of work unit IDs.
    """
    
    session=mturk.models.Session.objects.get(code=session_id);
    work_units=[];
    for w in session.mthit_set.all():
        work_units.append(w.ext_hitid);
    
    return work_units


@rpcmethod(name='mt.list_work_unit_submissions')
def list_work_unit_submissions(work_unit_extid):
    """Lists all submissions of a work unit. Only submission IDs are returned.
    @param work_unit_extid: The unique work unit ID.
    @return: [submission_id] - The list of submission IDs.
    """

    wu=mturk.models.WorkUnit.objects.get(ext_hitid=work_unit_extid);

    submissions=[];
    for s in wu.submittedtask_set.all():
        submissions.append(s.id);
    
    return submissions



@rpcmethod(name='mt.get_session')
def get_session(session_id):
    """Return session information by session code

    @param session_id: The ID of the session
    @return: Session"""
    
    session=mturk.models.Session.objects.get(code=session_id);
    
    return format_session(session)


@rpcmethod(name='mt.get_session_work_units')
def get_session_work_units(session_id):
    """Return all work units within session

    @param session_id: Session ID for which to list the work units
    @return: [work_units] - list of work units elements. """

    session=mturk.models.Session.objects.get(code=session_id);
    work_units=[];
    for w in session.mthit_set.all():
        work_units.append(format_work_unit(w));
    
    return work_units



@rpcmethod(name='mt.get_work_unit_submissions')
def get_work_unit_submissions(work_unit_extid):
    """Return all submissions for a work unit

    @param work_unit_extid: The work unit ID
    @return: [submissions] - list of work units submissions. """

    wu=mturk.models.WorkUnit.objects.get(ext_hitid=work_unit_extid);

    submissions=[];
    for s in wu.submittedtask_set.all():
        submissions.append(format_submission(s));
    
    return submissions





@rpcmethod(name='mt.get_work_unit_submissions_filtered')
def get_work_unit_submissions_filtered(work_unit_extid,filter):
    """Return filtered submissions for a work unit

    @param work_unit_extid: The work unit ID
    @param filter: (future) - good - only good, none - no filtering

    @return: [submissions] - list of work units submissions. """
    wu=mturk.models.WorkUnit.objects.get(ext_hitid=work_unit_extid);

    submissions=[];
    for s in wu.submittedtask_set.all():
        (grade,feedback) = get_submission_grade_pessimistic(s)
        if grade is not None and grade>7:
            submissions.append(format_submission(s));
    
    return submissions






@rpcmethod(name='mt.create_session', permission='mturk.add_session')
def create_session(code,task_id,crowd_engine,funding,work_unit_limit,qualifications,**kwargs):
    """Create session on the server.
    @param code: New session ID (must be unique)
    @param task_id: The ID of existing task
    @param crowd_engine: Which engine to use: "Internal", "MT_sandbox","MT_production"
    @param funding: Funding account ID.
    @param work_unit_limit: Max number of work units in the session
    @param qualifications: List of qualification IDs for the session.

    @return: Code of the created session
    """
    task=get_object_or_404(mturk.models.Task,name=task_id);
    funding=get_object_or_404(mturk.models.FundingAccount,name=funding);
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
def copy_session(prototype_session_id,new_session_id,**kwargs):
    """Duplicate a session. Create a new session with the same parameters as a source session.
    @param prototype_session_id: The ID of the source session
    @param new_session_id: The ID of the new session

    @return: New session ID or error.
    """
    session = get_object_or_404(mturk.models.Session,code=prototype_session_id);
    try:
        new_session = mturk.models.Session.objects.get(code=new_session_id)
        return 'Error: session exists'
    except:
        pass

    new_session=copy.copy(session);
    new_session.code=new_session_id;
    new_session.id = None;
    new_session.save();
    for q in session.mturk_qualification.all():
        new_session.mturk_qualification.add(q)
    return str(new_session.code)


@rpcmethod(name='mt.create_work_unit', permission='mturk.add_mthit')
def create_work_unit(session_id,parameters,shall_activate,**kwargs):
    """Create work unit
    @param session_id: ID of the session
    @param parameters: Raw parameter values
    @param shall_activate: Whether the task should be activated

    @return: HIT ID - unique ID of the task.
    """
    session=get_object_or_404(mturk.models.Session,code=session_id)

    if session.mthit_set.count()>=session.HITlimit:
        return "Error: HIT creation failed: maximum HIT count (%d) reached" % session.HITlimit

    id = session.mthit_set.count()+1;

    rand_id=str(uuid.uuid4())+"-"+str(id)

    hit=mturk.models.MTHit(session=session,ext_hitid=rand_id,int_hitid=id,parameters=parameters);
    hit.save();

    if not session.standalone_mode and shall_activate:
        created,ext_id = activate_hit(session,hit)
    else:
        ext_id = hit.ext_hitid

    return ext_id


def __generate_image_id(self,prefix=None):
    rand_id=str(uuid.uuid4())
    if prefix:
        return prefix+"-"+rand_id
    else:
        return rand_id

@rpcmethod(name='mt.post_image')
def post_image(session_id,img,image_name,reduce_jpeg_resolution=None,web_jpeg_quality=None,**kwargs):
    """Post an image to the server
    @param session_id: The session for the image
    @param img: raw image data
    @param image_name: The name for the image on the server
    @param reduce_jpeg_resolution: (optional,future) Reduce the resolution of the image on the server
    @param web_jpeg_quality: (optional,future) change image quality.

    @return: server image name
    """
    session=get_object_or_404(mturk.models.Session,code=session_id)

    if image_name is None or image_name=='' or image_name=='*AUTO':
        image_name=__generate_image_id()+".jpg"
    
    image_dir=os.path.join(settings.DATASETS_ROOT,session.code);
    if not os.path.exists(image_dir):
        os.makedirs(image_dir);
    image_file_name=os.path.join(image_dir,image_name)
    with open(image_file_name,'wb') as image_file:
        image_file.write(img.data);


    return image_name



@rpcmethod(name='mt.submit_work',permission='mturk.can_submit_work') #This is weaker than "add_submission"
def submit_work(work_unit_id,worker,assignment_id,data,**kwargs):
    """Submit work for a particular task.  

    This method allows for unit testing of the annotation handling and for
    automated task processing.
    
    @param work_unit_id: The work unit for which we submit work
    @param worker: worker ID
    @param assignment_id: Unique ID for the assignment (e.g. MechTurk AssignmentID)
    @param data: Submission data.

    @return: submission id
    """
    work_unit=get_object_or_404(mturk.models.WorkUnit,ext_hitid=work_unit_id);

    session=work_unit.session;

    GET={};
    POST=data;
    postS=pickler.dumps((GET,POST));
    submission=mturk.models.SubmittedTask(hit=work_unit,session_id=session.id,worker=worker,assignment_id=assignment_id, response=postS);
    submission.save();
    session.task_def.type.get_engine().on_submit(submission);

    work_unit.state=2; #Submitted
    work_unit.save();

    print "ROS ON SUBMISSION"
    ros_integration.on_submission(submission)

    return submission.id;



@rpcmethod(name='mt.submit_grade',permission='mturk.add_manualgraderecord')
def submit_grade(submission_id,quality,feedback,**kwargs):
    """Submit grade.  

    Allows the authenticated user to submit a grade. This API provides for integrated grading and faster grading or for automated external grading tools.
    """
    request=kwargs['request'];

    submission = get_object_or_404(mturk.models.SubmittedTask,id=submission_id)


    (worker,created)=mturk.models.Worker.objects.get_or_create(worker=request.user.username)
    if created and request.user.is_superuser:
        worker.utility = 100;
        worker.save()


    gr,created=mturk.models.ManualGradeRecord.objects.get_or_create(submission=submission,worker=worker)
    gr.quality=int(quality)
    gr.feedback=feedback
    gr.save();

    return True

@rpcmethod(name='mt.add_assignments')
def add_assignments(hit_ext_id,num_assignments,**kwargs):
    """Add turk assignments.  

    """
    request=kwargs['request'];

    hit = get_object_or_404(mturk.models.MTHit,ext_hitid=hit_ext_id);
    success,id= add_hit_assignments(hit.session,hit,num_assignments)
    return success


