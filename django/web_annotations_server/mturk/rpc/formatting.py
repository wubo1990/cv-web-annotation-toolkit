
"Internal package for mturk.rpc"


def format_session(session):
    """Formats the session as a dictionary object"""

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
    """Returns the current work unit state."""

    work_unit_state = work_unit_state_map[work_unit.state];
    if work_unit_state=='Active':
        num_valid_submissions=0;
        num_new_submissions=0;
        num_graded_submissions=0;
        num_good_submissions=0;
        for s in work_unit.submittedtask_set.filter(valid=True):
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
    """Returns formatted Work Unit representation."""

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
    """Returns formatted Submission representation."""

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
    """Returns formatted Grade representation."""
    grade_dict= {'id':grade.id,    
                 'quality':grade.quality,
                 'feedback':grade.feedback,
                 'worker':grade.worker,
                 'reference':grade.reference}
    return grade_dict


def get_submission_grade_pessimistic(st):
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


