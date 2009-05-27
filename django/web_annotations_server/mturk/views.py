# Create your views here.

import urllib,uuid,os,sys,shutil,subprocess
import cPickle as pickler

from django.conf import settings

from django.http import HttpResponse,Http404,HttpResponseRedirect
from django.shortcuts import render_to_response,get_object_or_404 
from django.views.generic.list_detail import object_list

try:
    from boto.mturk.connection import MTurkConnection
    from boto.mturk.question import ExternalQuestion
    from boto.mturk.qualification import Qualifications, PercentAssignmentsApprovedRequirement
    hasBoto=True
except Exception,e:
    print e
    
    hasBoto=False

from django.views.static import serve
import django


from models import *
#from annotation.datasets.views import get_frames_list_internal

#import mturk.protocols.people14.views as people14_views



##protocol_views={};
#protocol_views["person14"]=people14_views



def index(request):
    return HttpResponse("Here's the dummy view.")

"""
def showtask(request,protocol,session_code):
    print protocol
    print session_code
    try:
    	view_package=protocol_views[protocol];
    except :
        raise Http404

    session = get_object_or_404(CollectionSession,label=session_code)
    print session
    if 'workerId' in request.GET:
	workerId=request.GET['workerId'];
	task=models.select_next_task(session,workerId)
    else: 
	workerId=None
	task=models.select_sample_task(session)

    return view_package.showtask(request,protocol,session_code,task,workerId)

def report_result(request,session_code,task_id):
    return HttpResponse("Report results")	


def new_tasks_full(request,k_session,k_ds,k_protocol):
	session = get_object_or_404(CollectionSession,label=k_session)
	ds = get_object_or_404(Dataset,code=k_ds)
	protocol = get_object_or_404(AnnotationProtocol,code=k_protocol)

	frames=get_frames_list_internal(k_ds)
	for iFrame,frameName in enumerate(frames):
		task=AnnotationTask(collection_session=session,dataset=ds,protocol=protocol,dataunit=frameName)
		task.save();
	
	return HttpResponse("%d"%len(frames))
"""	
	
def load_tasks(request,k_session):
	print k_session
	session = get_object_or_404(Session,code=k_session)

	data_raw=request.POST['data'];
	data=urllib.unquote(data_raw);
	data=data.strip(" \n\t").split('\n')
	header=data[0].split('\t');
	tasks=data[1:];
	for iT, task in enumerate(tasks):
		args=task.split('\t');
		id=args[0]
		rand_id=str(uuid.uuid4())+"-"+id

		key_value_pairs=map(lambda k,v:k+"="+urllib.quote(v),header,args);
		params=reduce(lambda qs,p:qs+"&"+p,key_value_pairs);

		hit=MTHit(session=session,ext_hitid=rand_id,int_hitid=id,parameters=params);
		hit.save();
		print task
	
	return HttpResponse("%d" % len(tasks))
	
	
def showtask(request,session_code):    

    session = get_object_or_404(Session,code=session_code)
    session_parameters=session.parse_parameters();

    print len(session_parameters)

    if len(session_parameters)<=1:
        return showtask_new(request,session)

    protocol=session_parameters['protocol']
    taskurl=session_parameters['taskurl']


        

    url=taskurl
    if url.find("?")==-1:
	url=url+"?";

    hasTask=False;
    if 'ExtID' in request.GET:
	hasTask=True;
	task = get_object_or_404(MTHit,ext_hitid=request.GET['ExtID'])
	bFromGoldStandard=False;
	
    if 'workerId' in request.GET:
	workerId=request.GET['workerId'];
	worker,created=Worker.objects.get_or_create(session=session,worker=workerId);
	if created:
		worker.save();
	if not hasTask:
		(task,bFromGoldStandard)=select_next_task(session,workerId)
    	if url.endswith("?"):
		url=url+"wrkrating="+str(worker.utility)
    	else:
		url=url+"&wrkrating="+str(worker.utility)
    else: 
	workerId=None
	if not hasTask:
		task=select_sample_task(session)

    if task is None:
    	return render_to_response('mturk/not_available.html');

	
    if url.endswith("?"):
	url=url+"extid="+task.ext_hitid;
    else:
	url=url+"&extid="+task.ext_hitid;

    url=url+"&"+task.parameters
	
    url=url+"&session="+session.code;

    if 'mode' in request.POST:
	url=url+"&mode="+request.REQUEST['mode']

    for k,v in request.GET.items():	
	url=url+"&"+k+"="+v

    final_url=url;
    return HttpResponseRedirect(final_url)	



def showtask_new(request,session):

    url="/code/task.html?swf=label_generic"

    task = get_object_or_404(MTHit,ext_hitid=request.GET['ExtID'])

    if task is None:
    	return render_to_response('mturk/not_available.html');

	
    url=url+"&extid="+task.ext_hitid;

    url=url+"&session="+session.code;

    #url=url+"&"+task.parameters

    url=url+"&task="+session.task_def.name

    url=url+"&video="+session.code;
    url=url+"&frame="+task.parse_parameters()["frame"];
    url=url+"&img_base="+settings.HOST_NAME_FOR_MTURK;

    url=url+"&mode=MT2";
    url=url+"&swf_w=700&swf_h=700";
    url=url+"&instructions="+urllib.quote(session.task_def.instructions_url);
	
    for k,v in request.GET.items():	
	url=url+"&"+k+"="+v

    final_url=url;
    return HttpResponseRedirect(final_url)	



def show_task_for_hit(request,session_code,hit_int_id):
    session = get_object_or_404(Session,code=session_code)
    session_parameters=session.parse_parameters();
    protocol=session_parameters['protocol']
    taskurl=session_parameters['taskurl']


    url=taskurl
    if url.find("?")==-1:
	url=url+"?";

    if 'workerId' in request.GET:
	workerId=request.GET['workerId'];
    else:
	workerId="anonymous"

    task=get_object_or_404(MTHit,session=session,int_hitid=hit_int_id);
    worker,created=Worker.objects.get_or_create(session=session,worker=workerId);
    if created:
	worker.save();

    if task is None:
    	return render_to_response('mturk/not_available.html');


    if url.endswith("?"):
	url=url+"extid="+task.ext_hitid;
    else:
	url=url+"&extid="+task.ext_hitid;

    url=url+"&"+task.parameters
	
    url=url+"&session="+session.code;

    if 'mode' in request.REQUEST:
	url=url+"&mode="+request.REQUEST['mode']

    for k,v in request.GET.items():	
	url=url+"&"+k+"="+v

    final_url=url;
    return HttpResponseRedirect(final_url)	

def show_task_for_hit_ext(request,session_code,hit_id,ext_hitid):
    session = get_object_or_404(Session,code=session_code)
    task = get_object_or_404(MTHit,id=hit_id)
    if not task.ext_hitid==ext_hitid:
	raise Http404;

    session_parameters=session.parse_parameters();
    protocol=session_parameters['protocol']
    taskurl=session_parameters['taskurl']

    url=taskurl
    if url.find("?")==-1:
	url=url+"?";

    if 'workerId' in request.GET:
	workerId=request.GET['workerId'];
    else:
	workerId="anonymous"

    worker,created=Worker.objects.get_or_create(session=session,worker=workerId);
    if created:
	worker.save();

    if task is None:
    	return render_to_response('mturk/not_available.html');


    if url.endswith("?"):
	url=url+"extid="+task.ext_hitid;
    else:
	url=url+"&extid="+task.ext_hitid;

    url=url+"&"+task.parameters
	
    url=url+"&session="+session.code;

    if 'mode' in request.REQUEST:
	url=url+"&mode="+request.REQUEST['mode']

    for k,v in request.GET.items():	
	url=url+"&"+k+"="+v

    final_url=url;
    return HttpResponseRedirect(final_url)	

def send_hit_data(request,ext_id):
    task_id=ext_id;
    print task_id;
	 #request.REQUEST['extid']
    task = get_object_or_404(MTHit,ext_hitid=task_id);

    locations=get_existing_locations(task.session,task);
    str_response=""
    for l in locations:
	str_response=str_response+"%d %d 1\n"% l;
    #str_response="100 100 1\n200 200 2";

    return HttpResponse(str_response, mimetype="text/plain");


def submit_results_new(request,hit,session):

    workerId=request.REQUEST['workerId'];
    assignmentId=request.REQUEST['assignmentId'];


    if session.sandbox:
	submit_target="http://workersandbox.mturk.com/mturk/externalSubmit"
    else:
	submit_target="http://www.mturk.com/mturk/externalSubmit"


    postS=pickler.dumps((request.GET,request.POST))    
    submission=SubmittedTask(hit=hit,session_id=session.id,worker=workerId,assignment_id=assignmentId, response=postS);
    submission.save();


    if session.standalone_mode:
        return HttpResponseRedirect("/mt/get_task/"+session.code+"/" );
	


    return render_to_response('mturk/after_submit.html',
	{'submit_target':submit_target,
  	'extid': hit.ext_hitid, 'workerId':workerId,
	'assignmentId':assignmentId});



def submit_result(request):
    print request.POST
    task_id=request.REQUEST['extid']
    task = get_object_or_404(MTHit,ext_hitid=task_id)

    #The HIT can belong to some other session
    session_code=request.REQUEST['session']
    session = get_object_or_404(Session,code=session_code)

    sParm=session.parse_parameters();
    if len(sParm)<=1:
        return submit_results_new(request,task,session)



    #session = task.session;

    workerId=request.REQUEST['workerId'];
    assignmentId=request.REQUEST['assignmentId'];
    mode=request.REQUEST['mode'];
    if mode.endswith("sandbox") or mode.endswith("sandbox2"):
	submit_target="http://workersandbox.mturk.com/mturk/externalSubmit"
    else:
	submit_target="http://www.mturk.com/mturk/externalSubmit"

    if 'sandbox' in sParm:
	if int(sParm['sandbox']):
		submit_target="http://workersandbox.mturk.com/mturk/externalSubmit"

    postS=pickler.dumps((request.GET,request.POST))    
    submission=SubmittedTask(hit=task,session_id=session.id,worker=workerId,assignment_id=assignmentId, response=postS);
    submission.save();


    #Score the worker if we use gold standard
    if 'GS_session' in sParm:
	GoldStandard_session_code=sParm['GS_session'];
	GoldStandard_session = get_object_or_404(Session,code=GoldStandard_session_code)
	try:
		gold_standard_hit=GoldStandard_session.mthit_set.filter(int_hitid=task.int_hitid)[0];
    	
		worker,created=Worker.objects.get_or_create(session=session,worker=workerId);
    		report=score_worker(worker,gold_standard_hit,GoldStandard_session,task,session,submission)
		 
		gtURL="/mt/submission_gt_data/"+str(submission.id)+"/"+task.ext_hitid+"/";
		annURL="/mt/submission_data/"+str(submission.id)+"/"+task.ext_hitid+"/";
		comparison_list=urllib.quote_plus(annURL)+","+urllib.quote_plus(gtURL);
		
		protocol=sParm['protocol']
		if protocol=="people14":
			return render_to_response('protocols/people14/compare.html',
				{'submit_target':submit_target,
				'comparison_list':comparison_list,
			  	'extid': task_id, 'workerId':workerId,
				'grading_report' : report,
				'rating': worker.utility,
				'assignmentId'		:assignmentId,
				'parameters'		:task.parameters});

	except:
		#raise
		#Hit not in GS
		print "Hit not in GS"

    print sParm;
    if 'standalone_mode' in sParm:
	if int(sParm['standalone_mode']):
		return HttpResponseRedirect("/mt/get_task/"+session.code+"/" );
	


    return render_to_response('mturk/after_submit.html',
	{'submit_target':submit_target,
  	'extid': task_id, 'workerId':workerId,
	'assignmentId':assignmentId});


def view_submission(request,id,hitid=None):
	submission = get_object_or_404(SubmittedTask,id=int(id))
	if hitid is not None:
		if submission.hit.ext_hitid!=hitid:
			raise Http404
	session=submission.hit.session;
    	sParm=session.parse_parameters();
	protocol=sParm['protocol'];

	#gtURL="/mt/submission_gt_data/"+str(submission.id)+"/"+submission.hit.ext_hitid+"/";
	annURL="/mt/submission_data/"+str(submission.id)+"/"+submission.hit.ext_hitid+"/";
	#print gtURL
	print annURL
	#comparison_list=urllib.quote_plus(gtURL)+","+urllib.quote_plus(annURL);
	comparison_list=urllib.quote_plus(annURL)

	if protocol=="people14":
		return render_to_response('protocols/people14/compare.html',
				{'submit_target':None,
				'comparison_list':comparison_list,
				'parameters'		:submission.hit.parameters});
	else:	
		raise Http404


def get_submission_data(request,id=None,ext_hitid=None):
	submission = get_object_or_404(SubmittedTask,id=int(id))
	if not submission.hit.ext_hitid == ext_hitid:
		raise Http404
	
	locations=submission.get_parsed().shapes;
	print locations
	str_response=""
	if len(locations)>0:
	   for i,iL in enumerate(locations[0]['points']):
		if i>0:
			str_response=str_response+"\n"
		str_response=str_response+("%d,%d" % (iL[0],iL[1]))

    	return HttpResponse(str_response);

def get_submission_data_xml(request,id=None,ext_hitid=None):
	submission = get_object_or_404(SubmittedTask,id=int(id))
	#if not submission.hit.ext_hitid == ext_hitid:
	#	raise Http404
	
	str_response=submission.get_parsed().shapes;

    	return HttpResponse("<?xml version='1.0'?>\n"+str_response,mimetype="text/xml");

def get_submission_gt_data(request,id=None,ext_hitid=None):
	submission = get_object_or_404(SubmittedTask,id=int(id))
	if not submission.hit.ext_hitid == ext_hitid:
		raise Http404
	
	session=submission.hit.session;
	sParm=session.parse_parameters();
    	if 'GS_session' in sParm:
		GoldStandard_session_code=sParm['GS_session'];
		GoldStandard_session = get_object_or_404(Session,code=GoldStandard_session_code)
		try:
			gold_standard_hit=GoldStandard_session.mthit_set.filter(int_hitid=submission.hit.int_hitid)[0];
			locations=people14_get_gs_annotation(session,GoldStandard_session,gold_standard_hit);
		except:
			raise #debub
			raise Http404

		
	print locations
	str_response=""
	if len(locations)>0:
	   for i,iL in enumerate(locations[0]['points']):
		if i>0:
			str_response=str_response+"\n"
		str_response=str_response+("%d,%d" % (iL[0],iL[1]))

    	return HttpResponse(str_response, mimetype="text/plain");




def show_random_results(request,session_code):
	session = get_object_or_404(Session,code=session_code)
	protocol=session.parse_parameters()['protocol'];
    	results=session.submittedtask_set.all()[0:10];
	
	objects=[];
	for r in results:
		annURL="/mt/submission_data/"+str(r.id)+"/"+r.hit.ext_hitid+"/";
		comparison_list=urllib.quote_plus(annURL)
		objects.append({'submission':r,'url':comparison_list});

	return render_to_response('protocols/' +protocol+'/show_list.html',
				{'object_list':results});

def show_paged_results_base(request,session_code):
    return HttpResponseRedirect("p1/");

import math
def show_paged_results(request,session_code,page=1,order_by=None):
	session = get_object_or_404(Session,code=session_code)

	if len(session.parse_parameters())<=1:
		return show_paged_results_new(request,session,page,order_by)
	protocol=session.parse_parameters()['protocol'];

        if order_by:
            results=session.submittedtask_set.order_by(order_by);
        else:
            results=session.submittedtask_set.all();

	page_range=map(lambda x:int(math.floor(x/settings.NUM_HITS_PER_PAGE)+1),range(1,session.submittedtask_set.all().count(),settings.NUM_HITS_PER_PAGE));

	viewurl=s.hit.session.parse_parameters.viewurl
	return object_list(request,
                           queryset=results, 
                           paginate_by=settings.NUM_HITS_PER_PAGE, 
                           page=page,
                           template_name='protocols/' +protocol+'/show_list.html',
                           extra_context={'page_range':page_range,'viewurl':viewurl});


def show_sessions(request):
	sessions = Session.objects.all()
	return render_to_response('show_sessions.html', {'sessions':sessions})

def show_paged_results_new(request,session,page=1,order_by=None):
	protocol="g-xml"

        if order_by:
            results=session.submittedtask_set.order_by(order_by);
        else:
            results=session.submittedtask_set.all();

	page_range=map(lambda x:int(math.floor(x/settings.NUM_HITS_PER_PAGE)+1),range(1,session.submittedtask_set.all().count(),settings.NUM_HITS_PER_PAGE));

	return object_list(request,queryset=results, paginate_by=settings.NUM_HITS_PER_PAGE, page=page,
			template_name='protocols/' +protocol+'/show_list.html',extra_context={'page_range':page_range});

def show_most_recent_result(request,session_code,page=1):
	session = get_object_or_404(Session,code=session_code)
	protocol=session.parse_parameters()['protocol'];
    	results=get_most_recent_result(session);
	print results
        if results==None:
            raise Http404;
	
	page_range=map(lambda x:int(math.floor(x/settings.NUM_HITS_PER_PAGE)+1),range(1,session.submittedtask_set.all().count(),settings.NUM_HITS_PER_PAGE));

	return object_list(request,queryset=results, paginate_by=settings.NUM_HITS_PER_PAGE, page=page,
			template_name='protocols/' +protocol+'/show_list.html',extra_context={'refresh_rate':10000});

def grading_paged_base(request,session_code):
    return HttpResponseRedirect("p1/");

def grading_paged(request,session_code,page=1):
	session = get_object_or_404(Session,code=session_code)
        if len(session.parse_parameters())<=1:
            protocol="g-xml"
        else:
            protocol=session.parse_parameters()['protocol'];

    	results=session.submittedtask_set.all();

	return object_list(request,queryset=results, paginate_by=10, page=page,
			template_name='protocols/' +protocol+'/grading_list.html');


def grading_submit(request,submissionID):
	submission = get_object_or_404(SubmittedTask,id=submissionID)

	gr=ManualGradeRecord(submission=submission,
		quality=int(request.REQUEST['quality']),
		feedback=request.REQUEST['feedback'])
	gr.save();
	return HttpResponse("+")

def grading_report_reject(request,session_code):
	session = get_object_or_404(Session,code=session_code);
    	results=session.submittedtask_set.all()
	strAns="assignmentIdToReject\tassignmentIdToRejectComment\n";
	for r in results:
		grade=None
		feedback="";
		for g in r.manualgraderecord_set.all():
			grade=g.quality;
			feedback=g.feedback;
			break
		if grade is None:
			continue

		doReject=1;
		if grade>3:
			doReject=0;
		if not r.get_parsed().comments=="":
			doReject=0;
		if doReject:
			strAns=strAns+'%s\t"%s(let me know if you feel it\'s unfair)"\n'% (r.assignment_id,feedback)
	return HttpResponse(strAns)



def grading_report_approve(request,session_code):
	session = get_object_or_404(Session,code=session_code);
    	results=session.submittedtask_set.all()
	strAns="assignmentIdToApprove\tassignmentIdToApproveComment\n";
	for r in results:
		grade=None
		feedback="";
		for g in r.manualgraderecord_set.all():
			grade=g.quality;
			feedback=g.feedback;
			break
		if grade is None:
			continue

		doApprove=1;
		if grade<=3 and r.get_parsed().comments=="":
			doApprove=0;
		if doApprove:
			if grade<10:
				feedback=feedback+"There were some visible errors in the submission. "
			strAns=strAns+'%s\t"%s"\n'% (r.assignment_id,feedback)
	return HttpResponse(strAns)


def show_results_imagelist(request,session_code):
	session = get_object_or_404(Session,code=session_code);
    	results=session.submittedtask_set.all()
	strAns=""
	for r in results:
		strAns=r.hit.parameters+"\n"+strAns;

	return HttpResponse(strAns)



def get_perfect_results(request,session_code):
	session = get_object_or_404(Session,code=session_code);
    	results=session.submittedtask_set.all()
	strAns="";
	for r in results:
		grade=0
		for g in r.manualgraderecord_set.all():
			grade=max(grade,g.quality);

		doApprove=1;
		if grade<10:
			doApprove=0;
		if doApprove:
			shapes=r.get_parsed().shapes;
			d={};
			for pair in r.hit.parameters.split('&'):
				k,v=pair.split('=')
				d[k]=v;
			for s in shapes:
				str_box=""
				for pt in s['box']:
					str_box=str_box+("%d %d " % (pt[0],pt[1]));
				str_points=""
				for pt in s['points']:
					#str_points=str_points+",%s" % pt;
					str_points=str_points+"%s %s %s " % (pt[0],pt[1],pt[3]);
				strAns=strAns+'%d\t%s\t%s\t%s\t%s\t%s\n'% (r.id,d['id'],d['video'],d['frame'],str_box,str_points);
	return HttpResponse(strAns)


def get_non_perfect_results(request,session_code):
	session = get_object_or_404(Session,code=session_code);
    	hits=session.mthit_set.all()
	strAns="";
	response=HttpResponse();
	for h in hits:
		doApprove=0;

		for r in h.submittedtask_set.all():
			for g in r.manualgraderecord_set.all():
				if g.quality>9:
					doApprove=1;
					break
			if doApprove:
				break
		print h.id, doApprove
		if not doApprove:
			response.write("%d\t%s\t%s\n"% (h.id,h.int_hitid,h.ext_hitid));
	
	return response;


def stats_all(request):
	
	worker_contributions= stats_worker_contributions_perfect();
	submissions_per_session=stats_submissions_per_session();


	return render_to_response('mturk/stats_all.html',
				{'worker_contributions':worker_contributions,
				'submissions_per_session':submissions_per_session});


def grading_report_for_worker(request,worker_id):
	
	report= worker_grading_report_complete(worker_id)

	return render_to_response('mturk/worker_grading_report.html',
				{'report':report});



def newHIT(request):
	print request.POST
	session_code = request['session']
	frame = request['frame']
	try:
		original_name = request['original_name']
	except KeyError:
		original_name = frame

	session = get_object_or_404(Session,code=session_code)
    	session_parameters=session.parse_parameters();
    	protocol=session_parameters['protocol']
    	taskurl=session_parameters['taskurl']

	if 'HITlimit' not in session_parameters:
		HITlimit=100
	else:
		HITlimit=int(session_parameters['HITlimit']);

	if 'sandbox' not in session_parameters:
		sandbox_mode=1;
	else:
		sandbox_mode=int(session_parameters['sandbox']);
		
		
	print "HITlimit ",HITlimit

	if session.mthit_set.count()>=HITlimit:
		return HttpResponse("HIT creation failed: maximum HIT count (%d) reached" % HITlimit)

	if 'taskID' in request.GET:
		id = request['taskID']
	else:
		id = session.mthit_set.count()+1;

	rand_id=str(uuid.uuid4())+"-"+str(id)

	#key_value_pairs=['frame=':frame};
	#params=reduce(lambda qs,p:qs+"&"+p,key_value_pairs);
	
	params='frame='+frame+'&original_name='+original_name;

	hit=MTHit(session=session,ext_hitid=rand_id,int_hitid=id,parameters=params);
	hit.save();
	
	work_dir=settings.MTURK_WORK+session.code+'/';
	hit_files_dir=work_dir+rand_id+'/';
	if not os.path.exists(hit_files_dir):
		os.makedirs(hit_files_dir);

	shutil.copy(work_dir+'workload.properties',hit_files_dir);
	shutil.copy(work_dir+'workload.question',hit_files_dir);

	hInp=open(hit_files_dir+'workload.input','w');
	print >>hInp,"Id\tFrame\tExtID"
	print >>hInp,"%d\t%s\t%s" %(id,frame,hit.ext_hitid)
	hInp.close();

	if sandbox_mode:
		sandbox_str='-sandbox';
	else:
		sandbox_str='';
	print "SB:", sandbox_str
	cmd="%sMT_run2.sh %s %senv.source %s" % (settings.MTURK_ENV,hit_files_dir[0:-1],settings.MTURK_ENV,sandbox_str);
	print cmd
	os.system(cmd);

	#cmd="%ssubmit.py %s %s" % (settings.MTURK_ENV,hit_files_dir,settings.MTURK_ENV);
	#os.system(cmd);
	#subprocess.call(cmd, shell=True);
	#p = os.popen(cmd, shell=True)
	#sts = os.waitpid(p.pid, 0)

	
	return HttpResponse("HIT created: %s" % rand_id)




def newHIT2(request):
	print request.POST
	session_code = request['session']
	frame = request['frame']
	try:
		original_name = request['original_name']
	except KeyError:
		original_name = frame

	session = get_object_or_404(Session,code=session_code)


	if session.mthit_set.count()>=session.HITlimit:
		return HttpResponse("HIT creation failed: maximum HIT count (%d) reached" % session.HITlimit)

        id = session.mthit_set.count()+1;

	rand_id=str(uuid.uuid4())+"-"+str(id)

	

	image_dir=os.path.join(settings.DATASETS_ROOT,session.code);
        print image_dir
        if not os.path.exists(image_dir):
            os.makedirs(image_dir);

        image=request.FILES['image']
        hOut=open(os.path.join(image_dir,frame+".jpg"),'wb');
        hOut.write(image['content']);
        hOut.close();



	params='frame='+frame+'&original_name='+original_name;

	hit=MTHit(session=session,ext_hitid=rand_id,int_hitid=id,parameters=params);
	hit.save();

	


        taskurl=settings.HOST_NAME_FOR_MTURK+"mt/get_task/"+str(session.code)+"/?ExtID="+hit.ext_hitid;

        q = ExternalQuestion(external_url=taskurl, frame_height=800)

	if session.sandbox:
            awshost='mechanicalturk.sandbox.amazonaws.com'
        else:
            awshost='mechanicalturk.amazonaws.com'

        conn = MTurkConnection(host=awshost,aws_secret_access_key=session.funding.secret_key,aws_access_key_id=session.funding.access_key)

        keywords=session.task_def.get_keywords()

        t=session.task_def;
        if not t.hit_type:
            qualifications = Qualifications()
            qualifications.add(PercentAssignmentsApprovedRequirement(comparator="GreaterThan", integer_value="90"))



            create_hit_rs = conn.create_hit(question=q, 
                                            lifetime=t.lifetime,
                                            max_assignments=t.max_assignments,
                                            title=t.title,
                                            keywords=t.keywords,
                                            reward = t.reward,
                                            duration=t.duration,
                                            approval_delay=t.approval_delay, 
                                            annotation="IGNORE",
                                            qualifications=qualifications)
            assert(create_hit_rs.status == True)
            print create_hit_rs.HITTypeId
            t.hit_type=create_hit_rs.HITTypeId;
            t.save();
        else:
            create_hit_rs = conn.create_hit(question=q, hit_type=t.hit_type);

	return HttpResponse("%s" % hit.ext_hitid)



def get_hit_results_xml(request,ext_id):
    task_id=ext_id;
    print task_id;

	 #request.REQUEST['extid']
    task = get_object_or_404(MTHit,ext_hitid=task_id);
    print task

    s="";
    for st in task.submittedtask_set.all():
        s=s+st.get_parsed().shapes;
        print st

    if s=="":
        raise Http404;

    s="<annotations>"+s+"</annotations>";
    return HttpResponse(s, mimetype="text/plain");





def dynamic_task(request,path):
    print path[0:-4]
    objects=Task.objects.filter(name=path[0:-4])
    if len(objects)==0:
        return django.views.static.serve( request,path=path,document_root='/var/datasets/tasks/')
    else:
        return HttpResponse(str(objects[0].interface_xml), mimetype="text/xml");




def get_session_images(request,session_code):
	session = get_object_or_404(Session,code=session_code)

        response = HttpResponse();

	for hit in session.mthit_set.all():            
            parms=hit.parse_parameters();
            

            response.write("%s\t%smt/hit_results_xml/%s/\n" % (parms["original_name"],settings.HOST_NAME_FOR_MTURK,hit.ext_hitid))
        return response

def get_session_images_wget(request,session_code):
	session = get_object_or_404(Session,code=session_code)

        response = HttpResponse();

	for hit in session.mthit_set.all():            
            parms=hit.parse_parameters();
            
            local_name=parms["original_name"].replace("/","__").replace("\\","__");
            response.write("wget -O %s.results.xml %smt/hit_results_xml/%s/\n" % (local_name,settings.HOST_NAME_FOR_MTURK,hit.ext_hitid))
        return response


def reject_poor_results(request,session_code):
	session = get_object_or_404(Session,code=session_code);

        if session.sandbox:
            awshost='mechanicalturk.sandbox.amazonaws.com'
        else:
            awshost='mechanicalturk.amazonaws.com'

        conn = MTurkConnection(host=awshost,aws_secret_access_key=session.funding.secret_key,aws_access_key_id=session.funding.access_key)

     	results=session.submittedtask_set.all()
	strAns="assignmentIdToReject\tassignmentIdToRejectComment<br/>";
	for r in results:
		grade=None
		feedback="";
		for g in r.manualgraderecord_set.all():
                    if grade:
			if grade>g.quality:
                            grade=g.quality;
                            feedback=g.feedback;
                    else:
                        grade=g.quality;
			feedback=g.feedback;
		if grade is None:
			continue

		doReject=1;
		if grade>3:
			doReject=0;
		if not r.get_parsed().comments=="":
			doReject=0;
		if doReject:
                    try:
                        resp = conn.reject_assignment(r.assignment_id,feedback)
                        print resp
                        strAns=strAns+'Rejected: %s\t"%s"<br/>'% (r.assignment_id,feedback)
                    except e:
                        strAns=strAns+'Reject FAILED: %s\t"%s" : %s <br/>'% (r.assignment_id,feedback,str(e))
	return HttpResponse(strAns)




def approve_good_results(request,session_code):
	session = get_object_or_404(Session,code=session_code);

        if session.sandbox:
            awshost='mechanicalturk.sandbox.amazonaws.com'
        else:
            awshost='mechanicalturk.amazonaws.com'

        conn = MTurkConnection(host=awshost,aws_secret_access_key=session.funding.secret_key,aws_access_key_id=session.funding.access_key)

     	results=session.submittedtask_set.all()
	strAns="assignmentIdToReject\tassignmentIdToRejectComment<br/>";
	for r in results:
		grade=None
		feedback="";
		for g in r.manualgraderecord_set.all():
                    if grade:
			if grade>g.quality:
                            grade=g.quality;
                            feedback=g.feedback;
                    else:
                        grade=g.quality;
			feedback=g.feedback;
		if grade is None:
			continue

		doAccept=0;
		if grade>3:
			doAccept=1;
		if not r.get_parsed().comments=="":
			doAccept=1;
		if doAccept:
                    try:
                        resp = conn.approve_assignment(r.assignment_id,feedback)
                        print resp
                        strAns=strAns+'Approved: %s\t"%s"<br/>'% (r.assignment_id,feedback)
                    except e:
                        strAns=strAns+'Approve FAILED: %s\t"%s" : %s <br/>'% (r.assignment_id,feedback,str(e))
	return HttpResponse(strAns)




def approve_all_results(request,session_code):
	session = get_object_or_404(Session,code=session_code);

        if session.sandbox:
            awshost='mechanicalturk.sandbox.amazonaws.com'
        else:
            awshost='mechanicalturk.amazonaws.com'

        conn = MTurkConnection(host=awshost,aws_secret_access_key=session.funding.secret_key,aws_access_key_id=session.funding.access_key)

     	results=session.submittedtask_set.all()
	strAns="assignmentIdToReject\tassignmentIdToRejectComment<br/>";
	for r in results:
		grade=None
		feedback="";
		for g in r.manualgraderecord_set.all():
                    if grade:
			if grade>g.quality:
                            grade=g.quality;
                            feedback=g.feedback;
                    else:
                        grade=g.quality;
			feedback=g.feedback;
		#if grade is None:
		#	continue

		doAccept=1;
		if grade<=3:
                    doAccept=0;
		if not r.get_parsed().comments=="":
                    doAccept=1;
		if doAccept:
                    try:
                        resp = conn.approve_assignment(r.assignment_id,feedback)
                        print resp
                        strAns=strAns+'Approved: %s\t"%s"<br/>'% (r.assignment_id,feedback)
                    except e:
                        strAns=strAns+'Approve FAILED: %s\t"%s" : %s <br/>'% (r.assignment_id,feedback,str(e))
	return HttpResponse(strAns)



