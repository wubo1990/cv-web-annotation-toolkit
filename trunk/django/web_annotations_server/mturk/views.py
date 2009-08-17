# Create your views here.

import urllib,uuid,os,sys,shutil,subprocess,copy
import cPickle as pickler

from django.conf import settings
from django.core.files.storage import FileSystemStorage

from django.http import HttpResponse,Http404,HttpResponseRedirect
from django.shortcuts import render_to_response,get_object_or_404 
from django.views.generic.list_detail import object_list

from django.contrib.auth.decorators import login_required

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


try:
    from mturk.temp_rosnode import TmpNode

    ros_sender=TmpNode();
except:
    #print e.what()
    ros_sender=None




def index(request):
    return HttpResponse("Mechanical turk server.")


def main(request):
    if not request.user.is_anonymous():
        sessions=request.user.session_set.all().order_by('-id');
    else:
        sessions=[];
    return render_to_response('mturk/main.html',{'user':request.user,'sessions':sessions});

	
def get_task_parameters(request,task_name):
    task = get_object_or_404(Task,name=task_name)
    return HttpResponse(task.interface_xml,mimetype="text/xml");
	
def send_hit_parameters(request,ext_id):
    hit = get_object_or_404(MTHit,ext_hitid=ext_id)
    if hit.parameters.startswith("<?xml"):
        return HttpResponse(hit.parameters,mimetype="text/xml");
    else:
        return HttpResponse(hit.parameters,mimetype="text/plain");


def showtask(request,session_code):
    session = get_object_or_404(Session,code=session_code)

    task = get_object_or_404(MTHit,ext_hitid=request.GET['ExtID'])

    if task is None:
    	return render_to_response('mturk/not_available.html');

    te=task.session.task_def.type.get_engine();
    url=te.get_task_page_url(task,request);

    for k,v in request.GET.items():	
        url=url+"&"+k+"="+v

    final_url=url;
    return HttpResponseRedirect(final_url)	




def submit_result(request):

    print request.POST;

    task_id=request.REQUEST['extid']
    task = get_object_or_404(MTHit,ext_hitid=task_id)

    #The HIT can belong to some other session
    session_code=request.REQUEST['session']
    session = get_object_or_404(Session,code=session_code)

    workerId=request.REQUEST['workerId'];
    assignmentId=request.REQUEST['assignmentId'];


    if session.sandbox:
	submit_target="http://workersandbox.mturk.com/mturk/externalSubmit"
    else:
	submit_target="http://www.mturk.com/mturk/externalSubmit"

    hit = task;
    postS=pickler.dumps((request.GET,request.POST))    
    submission=SubmittedTask(hit=hit,session_id=session.id,worker=workerId,assignment_id=assignmentId, response=postS);
    submission.save();

    session.task_def.type.get_engine().on_submit(submission);
    if ros_sender:
        print "Sending results"

        try:
            xml_str=submission.get_parsed().shapes;
            params=hit.parse_parameters();

            img_size = params['image_size']
            img_name  = params['original_name']
            task_name = hit.session.task_def.name
            ref_frame = params['frame_id']
            ref_time = params['ref_time']
            ref_topic = params['topic_in']
            (secs,nsecs)=ref_time.split('.')

            img_size=[int(x) for x in img_size.split(',')]
            ros_sender.send(xml_str,img_size,secs,nsecs,task_name,ref_frame,ref_topic);
        except Exception:
            print "Failed to send the anntoation message. "

    if session.standalone_mode:
        return HttpResponseRedirect("/mt/get_task/"+session.code+"/" );
	


    return render_to_response('mturk/after_submit.html',
	{'submit_target':submit_target,
  	'extid': hit.ext_hitid, 'workerId':workerId,
	'assignmentId':assignmentId});




def get_submission_data_xml(request,id=None,ext_hitid=None):
	submission = get_object_or_404(SubmittedTask,id=int(id))
	
	str_response=submission.get_xml_str();

    	return HttpResponse(str_response,mimetype="text/xml");



def show_random_results(request,session_code):
	session = get_object_or_404(Session,code=session_code)
	protocol=session.task_def.type.name;
    	results=session.submittedtask_set.all()[0:10];
	
	objects=[];
	for r in results:
		annURL=r.get_persistent_url2();
		comparison_list=urllib.quote_plus(annURL)
		objects.append({'submission':r,'url':comparison_list});

	return render_to_response('protocols/' +protocol+'/show_list.html',
				{'object_list':results});

def show_paged_results_base(request,session_code):
    return HttpResponseRedirect("p1/");

import math

def show_sessions(request):
	sessions = Session.objects.all()
	return render_to_response('show_sessions.html', {'sessions':sessions})

def show_paged_results(request,session_code,page=1,order_by=None):
	session = get_object_or_404(Session,code=session_code)

	protocol=session.task_def.type.name;

        if order_by:
            results=session.submittedtask_set.order_by(order_by);
        else:
            results=session.submittedtask_set.all();

	page_range=map(lambda x:int(math.floor(x/settings.NUM_HITS_PER_PAGE)+1),range(1,session.submittedtask_set.all().count(),settings.NUM_HITS_PER_PAGE));

	return object_list(request,queryset=results, paginate_by=settings.NUM_HITS_PER_PAGE, page=page,
			template_name='protocols/' +protocol+'/show_list.html',extra_context={'page_range':page_range});



def show_good_results_paged_base(request,session_code):
    return HttpResponseRedirect("p1/");

def show_good_results_paged(request,session_code,page=1,order_by=None,num_per_page=None,template_name=None):
	session = get_object_or_404(Session,code=session_code)

	protocol=session.task_def.type.name;

        if order_by:
            results=session.submittedtask_set.order_by(order_by);
        else:
            results=session.submittedtask_set.all();

        results=results.filter(final_grade__gt=7);
        print results.count();

        if not num_per_page:
            num_per_page=settings.NUM_HITS_PER_PAGE;

	page_range=map(lambda x:int(math.floor(x/num_per_page)+1),range(1,results.count(),num_per_page));

        if not template_name:
            template_name='protocols/' +protocol+'/show_list.html'

	return object_list(request,queryset=results, paginate_by=num_per_page, page=page,
			template_name=template_name,extra_context={'page_range':page_range});


import math



def show_most_recent_result(request,session_code,page=1):
	session = get_object_or_404(Session,code=session_code)
	protocol=session.task_def.type.name;
    	results = get_most_recent_result(session);
	print results
        if results==None:
            raise Http404;
	
	page_range=map(lambda x:int(math.floor(x/settings.NUM_HITS_PER_PAGE)+1),range(1,session.submittedtask_set.all().count(),settings.NUM_HITS_PER_PAGE));

	return object_list(request,queryset=results, paginate_by=settings.NUM_HITS_PER_PAGE, page=page,
			template_name='protocols/' +protocol+'/show_list.html',extra_context={'refresh_rate':10000});

def show_sessions(request):
	sessions = Session.objects.all()
	return render_to_response('show_sessions.html', {'sessions':sessions})

def grading_paged_base(request,session_code):
    return HttpResponseRedirect("p1/");

def grading_paged(request,session_code,page=1):
	session = get_object_or_404(Session,code=session_code)
	protocol=session.task_def.type.name;

    	results=session.submittedtask_set.all();

	return object_list(request,queryset=results, paginate_by=10, page=page,
			template_name='protocols/' +protocol+'/grading_list.html');

def grading_thumbnail_random(request,session_code):
	session = get_object_or_404(Session,code=session_code)
	protocol=session.task_def.type.name;

    	results=session.submittedtask_set.all().extra(select={'rv':'RAND()'}).order_by('rv');

	return object_list(request,queryset=results, paginate_by=9, page=1,
			template_name='protocols/' +protocol+'/grading_thumbnail.html');


def grading_by_worker_paged_base(request,session_code,worker_code):
    return HttpResponseRedirect("p1/");

def grading_by_worker_paged(request,session_code,worker_code,page=1):
	session = get_object_or_404(Session,code=session_code)
	protocol=session.task_def.type.name;

        num_per_page=session.task_def.type.get_engine().get_internal_params().get('list_num_per_page',10)

    	results=session.submittedtask_set.all().filter(worker=worker_code);

	return object_list(request,queryset=results, paginate_by=num_per_page, page=page,
			template_name='protocols/' +protocol+'/grading_list.html');

@login_required
def grading_submit(request,submissionID):
	submission = get_object_or_404(SubmittedTask,id=submissionID)

        (worker,created)=Worker.objects.get_or_create(worker=request.user.username)
        if created and request.user.is_superuser:
            worker.utility = 100;
            worker.save()

	gr=ManualGradeRecord(submission=submission,
		quality=int(request.REQUEST['quality']),
		feedback=request.REQUEST['feedback'],
                       worker=worker);      
	gr.save();
	return HttpResponse("+")

def show_grading_conflict_details(request,session_code,grade_1_id,grade_2_id):
	session = get_object_or_404(Session,code=session_code)

    	results=get_grade_conflict_details(session,grade_1_id,grade_2_id)
	return render_to_response('mturk/conflict_details_list.html',
				{'session':session,'g1':grade_1_id,'g2':grade_2_id,'conflicts':results})

def grade_the_grading_by_worker_object(request,session_code,worker_code,task_id,grade):
	session = get_object_or_404(Session,code=session_code)
	grading_session = get_object_or_404(Session,code=session_code+"-grading")

    	results=get_grading_tasks_for_grading_submission(session,grading_session,worker_code,task_id)

	protocol=grading_session.task_def.type.name;

	return object_list(request,queryset=results, paginate_by=1, page=page,
                           template_name='protocols/' +protocol+'/grading_list.html');

def grading_by_submission_id(request,session_code,submission_id):
	session = get_object_or_404(Session,code=session_code)
	results = session.submittedtask_set.filter(id=submission_id)
        print results,session,submission_id
	protocol=session.task_def.type.name;

	return object_list(request,queryset=results, paginate_by=1, page=1,
                           template_name='protocols/' +protocol+'/grading_list.html');

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
	session_code = request.REQUEST['session']
	frame = request.REQUEST['frame']
	try:
		original_name = request.REQUEST['original_name']
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
        storage = FileSystemStorage(image_dir);
        path = storage.save(os.path.join(image_dir,frame+".jpg"),image);


    
        print "get_params"
        img_size = request.POST.get('image_size',"640,480")
        print "params"
        ref_frame = request.POST.get('frame_id','stereo_l_image_frame')
        ref_time = request.POST.get('ref_time','0.0')
        ref_topic = request.POST.get('topic_in','image_to_annotate')
        topic_out = request.POST.get('topic_out','annotation')

	params="frame="+frame+"&original_name="+original_name + \
            "&image_size=" + img_size + \
            "&frame_id=" + ref_frame + \
            "&ref_time=" + ref_time + \
            "&topic_in=" + ref_topic + \
            "&topic_out=" + topic_out 
        print params



        hit=MTHit(session=session,ext_hitid=rand_id,int_hitid=id,parameters=params);
	hit.save();

	if session.standalone_mode:
            return HttpResponse("%s" % hit.ext_hitid)

        taskurl=settings.HOST_NAME_FOR_MTURK+"mt/get_task/"+str(session.code)+"/?ExtID="+hit.ext_hitid;

        q = ExternalQuestion(external_url=taskurl, frame_height=800)

	if session.sandbox:
            awshost='mechanicalturk.sandbox.amazonaws.com'
        else:
            awshost='mechanicalturk.amazonaws.com'

        conn = MTurkConnection(host=awshost,aws_secret_access_key=session.funding.secret_key,aws_access_key_id=session.funding.access_key)

        keywords=session.task_def.get_keywords()

        t=session.task_def;
        if not session.hit_type:
            qualifications = Qualifications()
            qualifications.add(PercentAssignmentsApprovedRequirement(comparator="GreaterThan", integer_value="90"))



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
            assert(create_hit_rs.status == True)
            print create_hit_rs
            print create_hit_rs.HITTypeId
            session.hit_type=create_hit_rs.HITTypeId;
            session.save();
        else:
            create_hit_rs = conn.create_hit(question=q, hit_type=session.hit_type);
            print create_hit_rs

	return HttpResponse("%s" % hit.ext_hitid)


def new_HIT_generic(request):
	session_code = request.REQUEST['session']

	session = get_object_or_404(Session,code=session_code)


	if session.mthit_set.count()>=session.HITlimit:
		return HttpResponse("HIT creation failed: maximum HIT count (%d) reached" % session.HITlimit)

        id = session.mthit_set.count()+1;

	rand_id=str(uuid.uuid4())+"-"+str(id)

	
        params = request.REQUEST['parameters']

        hit=MTHit(session=session,ext_hitid=rand_id,int_hitid=id,parameters=params);
	hit.save();

	if session.standalone_mode:
            return HttpResponse("%s" % hit.ext_hitid)

        taskurl=settings.HOST_NAME_FOR_MTURK+"mt/get_task/"+str(session.code)+"/?ExtID="+hit.ext_hitid;

        q = ExternalQuestion(external_url=taskurl, frame_height=800)

	if session.sandbox:
            awshost='mechanicalturk.sandbox.amazonaws.com'
        else:
            awshost='mechanicalturk.amazonaws.com'

        conn = MTurkConnection(host=awshost,aws_secret_access_key=session.funding.secret_key,aws_access_key_id=session.funding.access_key)

        keywords=session.task_def.get_keywords()

        t=session.task_def;
        if not session.hit_type:
            qualifications = Qualifications()
            qualifications.add(PercentAssignmentsApprovedRequirement(comparator="GreaterThan", integer_value="90"))



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
            assert(create_hit_rs.status == True)
            print create_hit_rs
            print create_hit_rs.HITTypeId
            session.hit_type=create_hit_rs.HITTypeId;
            session.save();
        else:
            create_hit_rs = conn.create_hit(question=q, hit_type=session.hit_type);
            print create_hit_rs

	return HttpResponse("%s" % hit.ext_hitid)




def submit_redo_HITs(request,session_code):
    session = get_object_or_404(Session,code=session_code);

    hits=session.mthit_set.all();
    results=session.submittedtask_set.all();

    done_hits=hits.filter(submittedtask__manualgraderecord__quality__gt=7);
    hash_done_hits={};
    for h in done_hits:
        hash_done_hits[h.id]=1;
    print hash_done_hits
    print "Resubmitting %d tasks " % results.count();
    
    num_submitted=0;
    for hit in hits:
        if hit.id in hash_done_hits:
            print "Hit",hit.id ,"is done"
            continue
            
        taskurl=settings.HOST_NAME_FOR_MTURK+"mt/get_task/"+str(session.code)+"/?ExtID="+hit.ext_hitid;
        q = ExternalQuestion(external_url=taskurl, frame_height=800)

	if session.sandbox:
            awshost='mechanicalturk.sandbox.amazonaws.com'
        else:
            awshost='mechanicalturk.amazonaws.com'

        conn = MTurkConnection(host=awshost,aws_secret_access_key=session.funding.secret_key,aws_access_key_id=session.funding.access_key)
        t=session.task_def;
        if not session.hit_type:
            qualifications = Qualifications()
            qualifications.add(PercentAssignmentsApprovedRequirement(comparator="GreaterThan", integer_value="90"))
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
            assert(create_hit_rs.status == True)
            print create_hit_rs.HITTypeId
            session.hit_type=create_hit_rs.HITTypeId;
            session.save();
        else:
            create_hit_rs = conn.create_hit(question=q, hit_type=session.hit_type);
        print "Hit",hit.id ,"is submitted"

        num_submitted += 1;

    return HttpResponse("%d" % num_submitted)

def get_good_hit_results_xml(request,ext_id):
    return get_hit_results_xml(request,ext_id,True)

def get_hit_results_xml(request,ext_id,filterGood=False):
    task_id=ext_id;
    print task_id;

	 #request.REQUEST['extid']
    task = get_object_or_404(MTHit,ext_hitid=task_id);
    print task

    s="";
    for st in task.submittedtask_set.all():


        if filterGood:
            grade=None
            feedback="";
            for g in st.manualgraderecord_set.all():
                if grade:
                    if grade>g.quality:
                        grade=g.quality;
                        feedback=g.feedback;
                else:
                    grade=g.quality;
                    feedback=g.feedback;

            if grade is None:
                continue
            #Return only good. Skip "visible errors"
            print "Grade:",grade
            if grade <= 7:
                continue


        s=s+st.get_parsed().shapes;
        print st

    if s=="":
        raise Http404;

    if not s.startswith("<?"):
        s="<?xml version='1.0'?><annotations>"+s+"</annotations>";
    return HttpResponse(s, mimetype="text/xml");



@login_required
def grading_submit_session(request,session_code,grading_session_code):
    session = get_object_or_404(Session,code=session_code);

    try:
        grading_session = get_object_or_404(Session,code=grading_session_code);
    except Http404:
        if session_code+"-grading"==grading_session_code:
            print session.task_def.name+"-grading"
            task_def=get_object_or_404(Task,name=session.task_def.name+"-grading");
            grading_session = Session(code=grading_session_code,
                                      task_def=task_def,
                                      funding=session.funding,
                                      standalone_mode=session.standalone_mode,
                                      sandbox=session.sandbox,
                                      owner=session.owner)
            grading_session.save();

    if  request.user != session.owner and not request.user.is_superuser:
        raise Http404;


    stats={};
    stats['num_to_grade']=session.submittedtask_set.all().count();
    all_grading_items=[];
    for t in session.submittedtask_set.all():
        submission_id=session.code+"/"+ str(t.id)
        submission_url=t.get_grading_view_url();
        worker_id=t.worker
        print submission_id
        print submission_url
        all_grading_items.append([submission_id,submission_url,worker_id]);


    te=grading_session.task_def.type.get_engine();
    grading_params=te.reinterpret_task_parameters(grading_session.task_def)
    random.shuffle(all_grading_items);
    all_grading_items2=copy.copy(all_grading_items);
    random.shuffle(all_grading_items2);

    num_per_task1=int(grading_params["num_per_task"]*(1-grading_params["overlap"]));
    num_per_task2=int(grading_params["num_per_task"]-num_per_task1);

    num_tasks=int(math.ceil(float(len(all_grading_items))/num_per_task1));
    num_ok=0;
    num_failed=0;
    failed_msgs=[];
    for iTask in range(0,num_tasks):
        s1=iTask*num_per_task1
        e1=(iTask+1)*num_per_task1
        s2=iTask*num_per_task2
        e2=(iTask+1)*num_per_task2
        to_grade=[];
        to_grade.extend(all_grading_items[s1:e1]);
        to_grade.extend(all_grading_items2[s2:e2]);
        random.shuffle(to_grade);
        grade_xml="<?xml version='1.0'?><grading>"
        for t in to_grade:
            grade_xml+="<submission id='%s' url='%s' worker='%s'/>" % (t[0],urllib.quote(t[1]),t[2])
        grade_xml+="</grading>"

        (sts,msg)=add_hit_to_session(grading_session,grade_xml);
        if sts:
            num_ok+=1;
        else:
            num_failed+=1;
            failed_msgs.append({'msg':msg,'s':t})


    stats["num_submitted"]=num_ok;
    stats["num_failed"]=num_failed;

    return render_to_response('mturk/submitted_for_grading.html',{'user':request.user,'session':session,'grading_session':grading_session,'stats':stats,'failed_msgs':failed_msgs});


def add_hit_to_session(session,params):
    if session.mthit_set.count()>=session.HITlimit:
        return (False,"HIT creation failed: maximum HIT count (%d) reached" % session.HITlimit)

    id = session.mthit_set.count()+1;
    rand_id=str(uuid.uuid4())+"-"+str(id)
    hit=MTHit(session=session,ext_hitid=rand_id,int_hitid=id,parameters=params);
    hit.save();
    

    if session.standalone_mode:
        return (True,"%s" % hit.ext_hitid)

    taskurl=settings.HOST_NAME_FOR_MTURK+"mt/get_task/"+str(session.code)+"/?ExtID="+hit.ext_hitid;

    q = ExternalQuestion(external_url=taskurl, frame_height=800)

    if session.sandbox:
        awshost='mechanicalturk.sandbox.amazonaws.com'
    else:
        awshost='mechanicalturk.amazonaws.com'
        
    conn = MTurkConnection(host=awshost,aws_secret_access_key=session.funding.secret_key,aws_access_key_id=session.funding.access_key)

    keywords=session.task_def.get_keywords()

    t=session.task_def;
    if not session.hit_type:
        qualifications = Qualifications()
        qualifications.add(PercentAssignmentsApprovedRequirement(comparator="GreaterThan", integer_value="90"))
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
        assert(create_hit_rs.status == True)
        print create_hit_rs.HITTypeId
        session.hit_type=create_hit_rs.HITTypeId;
        session.save();
    else:
        create_hit_rs = conn.create_hit(question=q, hit_type=session.hit_type);
        print create_hit_rs
        print create_hit_rs.HITId

    hit.mt_hitid=create_hit_rs.HITId
    hit.save()
    return (True,"%s" % hit.ext_hitid)






def dynamic_task(request,path):
    print path[0:-4]
    objects=Task.objects.filter(name=path[0:-4])
    if len(objects)==0:
        return django.views.static.serve( request,path=path,document_root='/var/datasets/tasks/')
    else:
        return HttpResponse(str(objects[0].interface_xml), mimetype="text/xml");








def get_session_images2(request,session_code):
    return get_session_images(request,session_code,True)

def get_session_images3(request,session_code):
	session = get_object_or_404(Session,code=session_code)

        response = HttpResponse();

	for hit in session.mthit_set.all():            
            parms=hit.parse_parameters();
            
            frame=parms.get('frame','n/a');
            frame_id=parms.get('frame_id','n/a')
            ref_time=parms.get('ref_time','n/a')
            topic_in=parms.get('topic_in','n/a')
            original_name=parms.get('original_name','n/a')
            print parms
            response.write("%s\t/mt/good_hit_results_xml/%s/\t%s\t%s\t%s\t%s\t%s\t%s\n" % (settings.HOST_NAME_FOR_MTURK,hit.ext_hitid,session_code,frame,frame_id,ref_time,topic_in,original_name))

        return response


def get_session_good_results(request,session_code):
	session = get_object_or_404(Session,code=session_code)

        response = HttpResponse();

	for hit in session.mthit_set.all():            
            response.write("%s /mt/good_hit_results_xml/%s/ /mt/hit_parameters/%s/\n" % (hit.ext_hitid,hit.ext_hitid,hit.ext_hitid));

        return response





def get_session_images(request,session_code,filterGood=False):
	session = get_object_or_404(Session,code=session_code)

        response = HttpResponse();

	for hit in session.mthit_set.all():            
            parms=hit.parse_parameters();
            
            if filterGood:
                response.write("%s\t%smt/good_hit_results_xml/%s/\n" % (parms["original_name"],settings.HOST_NAME_FOR_MTURK,hit.ext_hitid))
            else:
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


@login_required
def reject_poor_results(request,session_code):
	session = get_object_or_404(Session,code=session_code);

        if session.sandbox:
            awshost='mechanicalturk.sandbox.amazonaws.com'
        else:
            awshost='mechanicalturk.amazonaws.com'

        conn = MTurkConnection(host=awshost,aws_secret_access_key=session.funding.secret_key,aws_access_key_id=session.funding.access_key)

     	results=session.submittedtask_set.all().exclude(state=4).exclude(state=3);
        te=session.task_def.type.get_engine();

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
		if doReject:
                    try:
                        resp = conn.reject_assignment(r.assignment_id,feedback)
                        r.valid=False;
                        r.state=4;
                        r.final_grade=str(grade);
                        r.save()
                        te.on_deactivate(r);
                        print resp
                        strAns=strAns+'Rejected: %s\t"%s"<br/>'% (r.assignment_id,feedback)
                    except Exception,e:
                        strAns=strAns+'Reject FAILED: %s\t"%s" : %s <br/>'% (r.assignment_id,feedback,str(e))
	return HttpResponse(strAns)






@login_required
def approve_good_results(request,session_code):
	session = get_object_or_404(Session,code=session_code);

        if session.sandbox:
            awshost='mechanicalturk.sandbox.amazonaws.com'
        else:
            awshost='mechanicalturk.amazonaws.com'

        conn = MTurkConnection(host=awshost,aws_secret_access_key=session.funding.secret_key,aws_access_key_id=session.funding.access_key)

     	results=session.submittedtask_set.all().exclude(state=4).exclude(state=3)
	strAns="assignmentIdToReject\tassignmentIdToRejectComment<br/>";
        te=session.task_def.type.get_engine();

	for r in results:
                print r.get_state_display()
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
		if grade>1 and not r.get_parsed().comments=="":
			doAccept=1;

		if doAccept:
                    try:
                        resp = conn.approve_assignment(r.assignment_id,feedback)
                        if r.valid and grade<10:
                            r.valid=False;
                            r.save()
                            te.on_deactivate(r);
                        print resp
                        strAns=strAns+'Approved: %s\t"%s"<br/>'% (r.assignment_id,feedback)
                        r.final_grade=str(grade);
                        r.state=3;
                        r.save();
                    except:
                        e = sys.exc_info()[1]
                        strAns=strAns+'Approve FAILED: %s\t"%s" : %s <br/>'% (r.assignment_id,feedback,str(e))
	return HttpResponse(strAns)



@login_required
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
            try:
                feedback="Automatic approval. "
                resp = conn.approve_assignment(r.assignment_id,feedback)
                print resp
                r.state=3;
                r.save();
                strAns=strAns+'Approved: %s\t"%s"<br/>'% (r.assignment_id,feedback)
            except:
                e = sys.exc_info()[1]
                strAns=strAns+'Approve FAILED: %s\t"%s" : %s <br/>'% (r.assignment_id,feedback,str(e))
	return HttpResponse(strAns)


@login_required
def approve_all_results_str(request,session):
        if session.sandbox:
            awshost='mechanicalturk.sandbox.amazonaws.com'
        else:
            awshost='mechanicalturk.amazonaws.com'

        conn = MTurkConnection(host=awshost,aws_secret_access_key=session.funding.secret_key,aws_access_key_id=session.funding.access_key)

     	results=session.submittedtask_set.all()
	strAns=""
	for r in results:
                    try:
                        feedback=""
                        resp = conn.approve_assignment(r.assignment_id,feedback)
                        print resp
                        strAns=strAns+'Approved: %s\t"%s"<br/>'% (r.assignment_id,feedback)
                    except:
                        e = sys.exc_info()[1]
                        strAns=strAns+'Approve FAILED: %s\t"%s" : %s <br/>'% (r.assignment_id,feedback,str(e))
	return strAns


@login_required
def approve_absolutely_all_results(request,magic_code):
    if not magic_code=="xxyyzz":
        return HttpResponse("done")

    sessions = Session.objects.all()
    r=HttpResponse();
    for s in sessions:
        r.write("Session: %s : "%s.code);
        r.write("\n<hr>\n");
        str_resp=approve_all_results_str(request,s)
        r.write(str_resp);
        r.write("\n<hr>\n");
        
    return r


@login_required
def deactivate_grade_record(request,grade_id):
    print grade_id
    grade_record = get_object_or_404(ManualGradeRecord,id=grade_id);
    grade_record.valid=False;
    grade_record.save()
    return HttpResponse("done")

@login_required
def expire_session_hits(request,session_code):
    session = get_object_or_404(Session,code=session_code);

    if session.sandbox:
        awshost='mechanicalturk.sandbox.amazonaws.com'
    else:
        awshost='mechanicalturk.amazonaws.com'
        
    conn = MTurkConnection(host=awshost,aws_secret_access_key=session.funding.secret_key,aws_access_key_id=session.funding.access_key)

    hits=session.mthit_set.all()[0:10]
    strAns=""
    for h in hits:
        print h
        

    return HttpResponse(strAns)



def get_ros_publishers(request):
    if not ros_sender:
        return HttpResponse("none")
    else:
        s=ros_sender.get_pub_string();
        return HttpResponse(s)






