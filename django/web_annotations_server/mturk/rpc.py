

from models import *
from common import *

from rpc4django import rpcmethod




@rpcmethod(name='mt.list_session_workunits')
def list_session_workunits(code):
    session=Session.objects.get(code=code);
    work_units=[];
    for w in session.mthit_set.all():
        work_units.append(w.ext_hitid);
    
    return work_units


@rpcmethod(name='mt.list_workunit_submissions')
def list_workunit_submissions(workunit_extid):
    wu=WorkUnit.objects.get(ext_hitid=workunit_extid);

    submissions=[];
    for s in wu.submittedtask_set.all():
        submissions.append(s.id);
    
    return submissions









@rpcmethod(name='mt.create_session')
def create_session(code,task_id,crowd_engine,funding,work_unit_limit):
    return "YEAH!"
"""
	code=models.SlugField();
	task_def=models.ForeignKey(Task);
	funding=models.ForeignKey(FundingAccount);

	standalone_mode = models.BooleanField(default=False);
	sandbox         = models.BooleanField(default=True);
	HITlimit        = models.IntegerField(default=100);
"""
