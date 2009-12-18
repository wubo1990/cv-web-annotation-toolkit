# Create your views here.

import urllib,uuid,os,sys,shutil,subprocess,copy
from PIL import Image
import cPickle as pickler

from django.conf import settings
from django.core.files.storage import FileSystemStorage

from django.http import HttpResponse,Http404,HttpResponseRedirect
from django.shortcuts import render_to_response,get_object_or_404 
from django.views.generic.list_detail import object_list

from django.contrib.auth.decorators import login_required
from subprocess import *

import yaml
import xml.sax.saxutils


try:
    from boto.mturk.connection import MTurkConnection
    from boto.mturk.question import ExternalQuestion
    from boto.mturk.qualification import Qualifications, PercentAssignmentsApprovedRequirement,Requirement
    from boto.mturk.qualification_type import *
    hasBoto=True
except Exception,e:
    print e
    
    hasBoto=False

from django.views.static import serve
import django


from models import *
from models_stats import *

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

@login_required
def main_all(request):
    sessions=Session.objects.all().order_by('-id');
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

def show_session_hits(request,session_code,hit_state,page=1):
    session = get_object_or_404(Session,code=session_code)
    if int(hit_state)>0:
        hits=session.mthit_set.filter(state=int(hit_state))
    else:
        hits=session.mthit_set.all();
    print session
    print hits
    
    num_per_page=session.task_def.type.get_engine().get_internal_params().get('list_num_per_page',settings.NUM_HITS_PER_PAGE)

    page_range=map(lambda x:int(math.floor(x/num_per_page)+1),range(1,session.submittedtask_set.all().count(),num_per_page));

    return object_list(request,queryset=hits, paginate_by=num_per_page, page=page,
                       template_name='mturk/session_hits_list.html',extra_context={'session':session,'page_range':page_range});




def showtask(request,session_code):
    if  0 and session_code=='willow-10-23-2009-s1-box':
        """This code immediately submits the result to MTurk without doing any work. This is a weird way to remove incorrectly submitted tasks form MTurk. Those will get auto-approved and paid by timeout."""
        """
        if 'workerId' in request.REQUEST:
            workerId=request.REQUEST["workerId"]
            ext_hitid=request.REQUEST['ExtID']
            assignmentId=request.REQUEST['assignmentId'];
            submit_target="http://www.mturk.com/mturk/externalSubmit"
            return render_to_response('mturk/after_submit.html',
                                      {'submit_target':submit_target,
                                       'extid': ext_hitid, 'workerId':workerId,
                                       'assignmentId':assignmentId});
        """
        pass
    session = get_object_or_404(Session,code=session_code)

    task = get_object_or_404(MTHit,ext_hitid=request.REQUEST['ExtID'])

    if "workerId" in request.REQUEST:
        worker_id=request.REQUEST["workerId"]
        print worker_id
        (worker,created)=Worker.objects.get_or_create(session=None,worker=worker_id)
        if created:
            worker.save();
        if worker.utility<settings.MTURK_BLOCK_WORKER_MIN_UTILITY:
            return render_to_response('mturk/not_available.html');

        exclusions=check_session_exclusions(worker,session);
        if len(exclusions)>0:
            reasons="";
            for e in exclusions:
                reasons += e[1];
                break;
            return render_to_response('mturk/not_available_excluded.html',{'reason':reasons} );

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



    if 'ExtID' in request.REQUEST:
        task_id=request.REQUEST['ExtID']
    else:
        task_id=request.REQUEST['extid']

    task = get_object_or_404(MTHit,ext_hitid=task_id)

    #The HIT can belong to some other session
    session = task.session;
    session_code=session.code;
    #session_code=request.REQUEST['session']
    #session = get_object_or_404(Session,code=session_code)

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


    if 'hitId' in request.REQUEST:
        mturk_hit_id=request.REQUEST['hitId']
        try:
            mthit=MechTurkHit.object.get(mechturk_hit_id=mturk_hit_id);
        except:
            mthit=None;
        if mthit:
            mthit.state=2; #Review
            mthit.save();

    session.task_def.type.get_engine().on_submit(submission);
    task.state=2; #Submitted
    task.save()




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



def get_rendered_submission(request,id=None,ext_hitid=None):
	submission = get_object_or_404(SubmittedTask,id=int(id))

	img_file = submission.hit.parse_parameters()["frame"];
	dataset_path=os.path.join(settings.DATASETS_ROOT,submission.session.code);
	image_filename=os.path.join(dataset_path,img_file+".jpg");
	im = Image.open(image_filename);	

	str_response=submission.get_xml_str();

	response = HttpResponse(mimetype="image/jpeg")
	im.save(response, "JPEG")

    	return response



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

        num_per_page=session.task_def.type.get_engine().get_internal_params().get('list_num_per_page',settings.NUM_HITS_PER_PAGE)

	page_range=map(lambda x:int(math.floor(x/num_per_page)+1),range(1,session.submittedtask_set.all().count(),num_per_page));

	return object_list(request,queryset=results, paginate_by=num_per_page, page=page,
			template_name='protocols/' +protocol+'/show_list.html',extra_context={'page_range':page_range});


def show_all_results(request,session_code):
        session = get_object_or_404(Session,code=session_code)
        protocol=session.task_def.type.name
        results=session.submittedtask_set.all()
        return object_list(request,queryset=results,template_name='protocols/'+protocol+'/grading_list.html');

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
            num_per_page=session.task_def.type.get_engine().get_internal_params().get('list_num_per_page',settings.NUM_HITS_PER_PAGE)


	page_range=map(lambda x:int(math.floor(x/num_per_page)+1),range(1,results.count(),num_per_page));

        if not template_name:
            template_name='protocols/' +protocol+'/show_list.html'

	return object_list(request,queryset=results, paginate_by=num_per_page, page=page,
			template_name=template_name,extra_context={'page_range':page_range});



def show_good_results_paged(request,session_code,page=1,filter=None,order_by=None,num_per_page=None,template_name=None):
	session = get_object_or_404(Session,code=session_code)

	protocol=session.task_def.type.name;

        if order_by:
            results=session.submittedtask_set.order_by(order_by);
        else:
            results=session.submittedtask_set.all();

        if filter is None:
            results=results.filter(final_grade__gt=7);
        else:
            results=results.filter(final_grade__gt=7,hit__parameters__like=filter);

        print results.count();

        if not num_per_page:
            num_per_page=session.task_def.type.get_engine().get_internal_params().get('list_num_per_page',settings.NUM_HITS_PER_PAGE)

	page_range=map(lambda x:int(math.floor(x/num_per_page)+1),range(1,results.count(),num_per_page));

        if not template_name:
            template_name='protocols/' +protocol+'/show_list.html'

	return object_list(request,queryset=results, paginate_by=num_per_page, page=page,
			template_name=template_name,extra_context={'page_range':page_range});




def show_good_results_w_filter_paged(request,session_code,page=1,filter=None,order_by=None,num_per_page=None,template_name=None):
        session = get_object_or_404(Session,code=session_code)

        protocol=session.task_def.type.name;

        if order_by:
            results=session.submittedtask_set.order_by(order_by);
        else:
            results=session.submittedtask_set.all();

        #results=results.filter(final_grade__gt=7,hit__parameters__contains=filter);
        results=results.filter(hit__parameters__contains=filter);
        print results.count();

        if not num_per_page:
            num_per_page=session.task_def.type.get_engine().get_internal_params().get('list_num_per_page',settings.NUM_HITS_PER_PAGE)

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
	
        num_per_page=session.task_def.type.get_engine().get_internal_params().get('list_num_per_page',settings.NUM_HITS_PER_PAGE)

	page_range=map(lambda x:int(math.floor(x/num_per_page)+1),range(1,session.submittedtask_set.all().count(),num_per_page)); 
        

	return object_list(request,queryset=results, paginate_by=num_per_page, page=page,
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

def grading_by_worker_no_session_paged_base(request,session_code,worker_code):
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


def grading_by_worker_no_session_paged(request,worker_code,page=1):
	session = get_object_or_404(Session,code=session_code)
	protocol=session.task_def.type.name;

        num_per_page=10

    	results=Submittedtask.objects.filter(worker=worker_code);
        protocol="gxml"
	return object_list(request,queryset=results, paginate_by=num_per_page, page=page,
			template_name='protocols/' +protocol+'/grading_list.html');




@login_required
def adjudicate_by_submission_id(request,session_code,submission_id):
	session = get_object_or_404(Session,code=session_code)
	results = session.submittedtask_set.filter(id=submission_id)
        print results,session,submission_id
	protocol=session.task_def.type.name;

	return object_list(request,queryset=results, paginate_by=1, page=1,
                           template_name='protocols/' +protocol+'/grading_list2.html');


@login_required
def adjudicate_by_conflict_type(request,session_code,grade_A,grade_B,page=1):
	session = get_object_or_404(Session,code=session_code)

        submission_ids=get_grade_conflict_submission_list(session,grade_A,grade_B);
	results = session.submittedtask_set.filter(id__in=submission_ids)

	protocol=session.task_def.type.name;

	return object_list(request,queryset=results, paginate_by=10, page=page,
                           template_name='protocols/' +protocol+'/grading_list2.html');



@login_required
def adjudicate_submit(request,submissionID):
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
        nChanged=0;
        for grade in submission.manualgraderecord_set.all():
            if grade.quality <> gr.quality:
                grade.valid = False;
                grade.save();
                nChanged += 1;

	return HttpResponse("+ %d" % nChanged)



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
		if grade<=3:
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
@login_required
def ban_worker(request,worker_id):
    worker=get_object_or_404(Worker,session=None,worker=worker_id);
    worker.utility=0;
    worker.save();

    return HttpResponse("banned");

@login_required
def unban_worker(request,worker_id):
    worker=get_object_or_404(Worker,session=None,worker=worker_id);
    worker.utility=50;
    worker.save();

    return HttpResponse("unbanned");


def grading_report_for_worker(request,worker_id):
	
	report= worker_grading_report_complete(worker_id)

	return render_to_response('mturk/worker_grading_report.html',
				{'report':report});



def add_session_qualifications(qualifications,session,force_create=False):
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
        if 'reduce-quality' in request.REQUEST or 'reduce-resolution' in request.REQUEST:
            quality=request.REQUEST.get('reduce-quality',None)
            resolution=request.REQUEST.get('reduce-resolution',None)
            path = storage.save(os.path.join(image_dir,frame+"-original.jpg"),image);
            img=Image.open(os.path.join(image_dir,frame+"-original.jpg"));
            if resolution:
                (newW,newH)=map(lambda s:float(s),resolution.split("x"));
                img = img.resize((newW,newH),Image.BICUBIC)
            if quality:
                img.save(os.path.join(image_dir,frame+".jpg"),"JPEG",quality=int(quality));                
            else:
                img.save(os.path.join(image_dir,frame+".jpg"))

        else:
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
            print pickler.dumps(create_hit_rs)
            assert(create_hit_rs.status == True)
            print create_hit_rs
            print create_hit_rs.HITTypeId
            session.hit_type=create_hit_rs.HITTypeId;
            session.save();
        else:
            create_hit_rs = conn.create_hit(question=q, hit_type=session.hit_type);
            #print pickler.dumps(create_hit_rs)

        mt_hit_id=create_hit_rs.HITId
        mthit=MechTurkHit(session=session,mthit=hit,state=1,mechturk_hit_id=mt_hit_id); #state=Active
        mthit.save();
        
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
            assert(create_hit_rs.status == True)
            print create_hit_rs
            print create_hit_rs.HITTypeId
            session.hit_type=create_hit_rs.HITTypeId;
            session.save();
        else:
            create_hit_rs = conn.create_hit(question=q, hit_type=session.hit_type);
            print create_hit_rs

        mt_hit_id=create_hit_rs.HITId
        mthit=MechTurkHit(session=session,mthit=hit,state=1,mechturk_hit_id=mt_hit_id); #state=Active
        mthit.save();

	return HttpResponse("%s" % hit.ext_hitid)


@login_required
def force_update_session_HITType(request,session_code):
    session = get_object_or_404(Session,code=session_code)

    if session.standalone_mode:
        return HttpResponse("- The session is standalone. Can not update")


    old_hit_type = session.hit_type
    try:
        new_hit_type = create_session_hit_type(session)
    except MTurkException:
        return HttpResponse("- Failed to create hit type");
        

    (num_affected,num_failures)=update_session_hittype(session,new_hit_type);
    return HttpResponse("+ affected %d num_failures %d"%( num_affected,num_failures))

@login_required
def force_update_task_HITType(request,task_code):
    task = get_object_or_404(Task,name=task_code)

    tot_num_affected = 0;
    tot_num_failures = 0;
    for session in task.session_set.all():
        if session.standalone_mode:
            print ("- The session is standalone. Can not update")
            continue
        old_hit_type = session.hit_type
        try:
            new_hit_type = create_session_hit_type(session)
        except MTurkException:
            print "- Failed to create hit type";
            continue

        (num_affected,num_failures)=update_session_hittype(session,new_hit_type);
        tot_num_affected += num_affected
        tot_num_failures += num_failures

    return HttpResponse("+ affected %d num_failures %d"%( tot_num_affected,tot_num_failures))


def update_session_hittype(session,new_hit_type):
    session.hit_type = new_hit_type;
    session.save()
    hits=session.mechturkhit_set.all()

    conn = get_mt_connection(session)    
    num_failures =0;
    num_affected=0;
    for h in hits:
        print h.mechturk_hit_id
        try:
            rs = change_hit_type(conn,h.mechturk_hit_id,new_hit_type)
            print rs
            num_affected+=1;
        except MTurkException :
            num_failures+=1;
    return (num_affected,num_failures)




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

    conn = MTurkConnection(host=awshost,aws_secret_access_key=session.funding.secret_key,aws_access_key_id=session.funding.access_key)
    return conn

def create_session_hit_type(session,force_create_qualifications=False):

    conn = get_mt_connection(session)

    keywords=session.task_def.get_keywords()

    t=session.task_def;
    qualifications = Qualifications()
    qualifications.add(PercentAssignmentsApprovedRequirement(comparator="GreaterThan", integer_value="90"))

    qualifications=add_session_qualifications(qualifications,session,force_create_qualifications);
    print qualifications.get_as_params()
    create_hit_rs = conn.register_hit_type(  title=t.title,
                                             description=t.description,
                                            keywords=str(t.keywords),
                                            reward = t.reward,
                                            duration=t.duration,
                                            approval_delay=t.approval_delay, 
                                            qual_req=qualifications)
    if (create_hit_rs.status != True):
        raise MTurkException(create_hit_rs);


    print "Created HIT Type",create_hit_rs.HITTypeId
    hit_type_id=create_hit_rs.HITTypeId;
    return hit_type_id

def copy_session(request,prototype_session_code,new_session_code):
    session = get_object_or_404(Session,code=prototype_session_code);
    try:
        new_session = Session.objects.get(code=new_session_code)
        return HttpResponse("- %d\nAlready exists" % new_session.id)
    except:
        pass

    new_session=copy.copy(session);
    new_session.code=new_session_code;
    new_session.id = None;
    new_session.save();
    return HttpResponse("+ %d" % new_session.id)

def submit_redo_HITs(request,session_code):
    session = get_object_or_404(Session,code=session_code);

    hits=session.mthit_set.all();
    results=session.submittedtask_set.all();

    done_hits=hits.filter(submittedtask__manualgraderecord__quality__gt=7);
    hash_done_hits={};
    for h in done_hits:
        done=False
        for s in h.submittedtask_set.all():
            for g in s.manualgraderecord_set.all():
                if g.valid and g.quality>7:
                    print s.id,g.quality,g.valid,g.id,h.id
                    done=True
                    break
        if done:
            hash_done_hits[h.id]=1;
    print hash_done_hits
    print "Resubmitting %d tasks " % results.count();
    
    num_submitted=0;
    for hit in hits:
        if hit.id in hash_done_hits:
            print "Hit",hit.id ,"is done"
            continue
        print hit.id," is not done"
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

            add_session_qualifications(qualifications,session);
            print t.reward
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
            #postS=pickler.dumps(create_hit_rs)
            #print postS
            assert(create_hit_rs.status == True)
            print create_hit_rs.HITTypeId
            session.hit_type=create_hit_rs.HITTypeId;
            session.save();
        else:
            create_hit_rs = conn.create_hit(question=q, hit_type=session.hit_type);
        print dir(create_hit_rs)

        print "Hit",hit.id ,"is submitted"
        hit.state=6;
        hit.save();

        mt_hit_id=create_hit_rs.HITId
        mthit=MechTurkHit(session=session,mthit=hit,state=1,mechturk_hit_id=mt_hit_id); #state=Active
        mthit.save();

        #print create_hit_rs
        #postS=pickler.dumps(create_hit_rs)
        #print postS
        #print create_hit_rs.HITId

        num_submitted += 1;

    return HttpResponse("%d" % num_submitted)

def get_good_hit_results_xml(request,ext_id):
    return get_hit_results_xml(request,ext_id,True)

def get_hit_results_xml(request,ext_id,filter_good_results=False):
    task_id=ext_id;
    print task_id;

	 #request.REQUEST['extid']
    task = get_object_or_404(MTHit,ext_hitid=task_id);
    print task

    s="";
    for st in task.submittedtask_set.all():

        print st.id,st.final_grade 

        if filter_good_results:
            grade_xml="<grades>"
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
                grade_xml+="<grade value='%d'/>" % g.quality
            grade_xml+="</grades>"

            if grade is None:
                continue
            #Return only good. Skip "visible errors"
            print "Grade:",grade
            if grade <= 7:
                continue


        s=s+st.get_parsed().shapes;

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
        if session_code+"-grading"==grading_session_code or session_code+"-grading-2"==grading_session_code:
            print session.task_def.name+"-grading"
            task_def=get_object_or_404(Task,name=session.task_def.name+"-grading");
            grading_session = Session(code=grading_session_code,
                                      task_def=task_def,
                                      funding=session.funding,
                                      standalone_mode=session.standalone_mode,
                                      sandbox=session.sandbox,
                                      owner=session.owner)
            grading_session.save();
            exclude=SessionExclusion(session_A=session,session_B=grading_session,decline_reason="You can't do grading, because you submitted work in this session.");
            exclude.save();
            other_grading_sessions=Session.objects.filter(code__startswith=session_code+"-grading");
            for other_session in other_grading_sessions:
                if other_session.code == grading_session.code:
                    continue
                exclude=SessionExclusion(session_A=other_session,session_B=grading_session,decline_reason="Participation in two review sessions isn't allowed.");
                exclude.save();
                exclude=SessionExclusion(session_A=grading_session,session_B=other_session,decline_reason="Participation in two review sessions isn't allowed.");
                exclude.save();

    if  request.user != session.owner and not request.user.is_superuser:
        raise Http404;


    te=grading_session.task_def.type.get_engine();
    grading_params=te.reinterpret_task_parameters(grading_session.task_def)

    stats={};
    stats['num_to_grade']=session.submittedtask_set.filter(state__in=[1,2]).count();
    all_grading_items=[];
    #for t in session.submittedtask_set.all():
    for t in session.submittedtask_set.filter(state__in=[1,2]):
        submission_id=session.code+"/"+ str(t.id)
        submission_url=t.get_grading_view_url(grading_params);
        worker_id=t.worker
        print submission_id
        print submission_url
        all_grading_items.append([submission_id,submission_url,worker_id]);

    """initial_te=session.task_def.type.get_engine();
    if "frame_w" in initial_te.get_internal_params() and "frame_h" in initial_te.get_internal_params():
        w=initial_te.get_internal_params()["frame_w"]
        h=initial_te.get_internal_params()["frame_h"]
        """


    random.shuffle(all_grading_items);
    all_grading_items2=copy.copy(all_grading_items);
    random.shuffle(all_grading_items2);

    num_per_task1=int(grading_params["num_per_task"]*(1-grading_params["overlap"]));
    num_per_task2=int(grading_params["num_per_task"]-num_per_task1);

    frame_str = ' frame_w="%d" frame_h="%d"' % (grading_params["frame_w"],grading_params["frame_h"]);


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
            grade_xml+="<submission id='%s' url='%s' worker='%s' %s/>" % (t[0],urllib.quote(t[1]),t[2],frame_str)
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
        assert(create_hit_rs.status == True)
        print create_hit_rs.HITTypeId
        session.hit_type=create_hit_rs.HITTypeId;
        session.save();
    else:
        create_hit_rs = conn.create_hit(question=q, hit_type=session.hit_type);
        print create_hit_rs
        print create_hit_rs.HITId

    #hit.mt_hitid=create_hit_rs.HITId
    hit.save()

    mt_hit_id=create_hit_rs.HITId
    mthit=MechTurkHit(session=session,mthit=hit,state=1,mechturk_hit_id=mt_hit_id);
    mthit.save();

    return (True,"%s" % hit.ext_hitid)



def activate_hit(session,hit):
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
        assert(create_hit_rs.status == True)

        session.hit_type=create_hit_rs.HITTypeId;
        session.save();
    else:
        create_hit_rs = conn.create_hit(question=q, hit_type=session.hit_type);

    try:
        mt_hit_id=create_hit_rs.HITId
    except:
        return (False,None);
    else:
        mthit=MechTurkHit(session=session,mthit=hit,state=1,mechturk_hit_id=mt_hit_id);
        mthit.save();

        hit.state=6 #Active.
        hit.save();

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
            image_dir=os.path.join(settings.DATASETS_ROOT,session.code);
            original_fn =os.path.join(image_dir,frame+"-original.jpg");
            if os.path.exists(original_fn):
                img_id=frame+"-original"
            else:
                img_id=frame

            response.write("%s\t/mt/good_hit_results_xml/%s/\t%s\t%s\t%s\t%s\t%s\t%s\n" % (settings.HOST_NAME_FOR_MTURK,hit.ext_hitid,session_code,img_id,frame_id,ref_time,topic_in,original_name))

        return response


#def get_session_images4(request,session_code):
def get_session_work_units(request,session_code):
	session = get_object_or_404(Session,code=session_code)

        results={};
	for hit in session.mthit_set.all():            
            parms=hit.parse_parameters();

            hit_d={};
            frame=parms.get('frame',None);
            if frame:
                hit_d['frame']=frame
            frame_id=parms.get('frame_id',None)
            if frame_id:
                hit_d['frame_id']=frame_id
            ref_time=parms.get('ref_time',None)
            if ref_time:
                hit_d['ref_time']=ref_time
            topic_in=parms.get('topic_in',None)
            if topic_in:
                hit_d['topic_in']=topic_in
            original_name=parms.get('original_name',None)
            if original_name:
                hit_d['original_name']=original_name

            image_dir=os.path.join(settings.DATASETS_ROOT,session.code);
            original_fn =os.path.join(image_dir,frame+"-original.jpg");
            if os.path.exists(original_fn):
                img_id=frame+"-original"
            else:
                img_id=frame
            
            hit_d['int_id']=hit.id;
            hit_d['ext_work_unit_id']=hit.ext_hitid;
            hit_d['image_id']=img_id;
            results[hit.ext_hitid]=hit_d

        resp=HttpResponse()
        resp.write(yaml.dump(results));
        return resp;


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
        print results.count()
        te=session.task_def.type.get_engine();

	strAns="assignmentIdToReject\tassignmentIdToRejectComment<br/>";
	for r in results:
		grade=None
		feedback="";
                num_inactive=0;
		for g in r.manualgraderecord_set.all():
                    if not g.valid:
                        num_inactive+=1;
                        continue
                    if grade:
			if grade>g.quality:
                            grade=g.quality;
                            feedback=g.feedback;
                    else:
                        grade=g.quality;
			feedback=g.feedback;
		if grade is None:
                    print "Result ",r.id,"doesn't has no grades (",num_inactive," inactive)"
                    continue
                else:
                    print "Result ",r.id,"has grade ",grade

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

                        r.hit.state=5; # Open
                        r.hit.save();
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

     	#results=session.submittedtask_set.all()
     	results=session.submittedtask_set.all().exclude(state=4).exclude(state=3)
	strAns="assignmentIdToReject\tassignmentIdToRejectComment<br/>";
        te=session.task_def.type.get_engine();

	for r in results:
                print r.get_state_display()
		grade=None
		feedback="";
		for g in r.manualgraderecord_set.all():
                    if not g.valid:
                        continue

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

		if doAccept:
                    try:
                        resp = conn.approve_assignment(r.assignment_id,feedback)
                        if r.valid and grade<10:
                            r.valid=False;
                            r.state=3
                            r.save()
                            te.on_deactivate(r);
                        print resp
                        strAns=strAns+'Approved: %s\t"%s"<br/>'% (r.assignment_id,feedback)
                        r.final_grade=str(grade);
                        r.state=3;
                        r.save();
                        if grade<10:
                            r.hit.state=5; # Open
                        else:
                            r.hit.state=4; # Finalized
                        r.hit.save();
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
                r.hit.state=4; # Finalized
                r.hit.save();
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



def get_submission_valid_grades(request,id):
	submission = get_object_or_404(SubmittedTask,id=id);
        results=[];
        for g in submission.manualgraderecord_set.all():
            if not g.valid:
                continue
            results.append(g.to_dict())
        
        resp=HttpResponse()
        resp.write(yaml.dump(results));
        return resp;

def session_stats(request,session_code):
    session = get_object_or_404(Session,code=session_code);
    stats = hit_counts_by_state(session)

    resp=HttpResponse()
    resp.write(yaml.dump(stats));
    return resp;


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


@login_required
def expire_session_hits(request,session_code):
    session = get_object_or_404(Session,code=session_code);

    if session.sandbox:
        awshost='mechanicalturk.sandbox.amazonaws.com'
    else:
        awshost='mechanicalturk.amazonaws.com'
        
    conn = MTurkConnection(host=awshost,aws_secret_access_key=session.funding.secret_key,aws_access_key_id=session.funding.access_key)

    hits=session.mechturkhit_set.all()
    
    num_skipped =0;
    num_affected=0;
    for h in hits:
        if h.state==1:
            print conn,h.mechturk_hit_id
            print expire_hit(conn,h.mechturk_hit_id)
            h.state=5
            h.save()
            num_affected+=1;
        else:
            num_skipped +=1;

    return HttpResponse("+ affected %d, skipped %d"%( num_affected, num_skipped))


@login_required
def expire_session_hits_by_type(request,session_code):
    session = get_object_or_404(Session,code=session_code);

    if session.sandbox:
        awshost='mechanicalturk.sandbox.amazonaws.com'
    else:
        awshost='mechanicalturk.amazonaws.com'
        
    conn = MTurkConnection(host=awshost,aws_secret_access_key=session.funding.secret_key,aws_access_key_id=session.funding.access_key)

    resp=HttpResponse();
    total_num_results = None
    last_page = None
    page=1;
    page_size = 20;
    counts={};
    num_affected=0;
    num_skipped_by_type=0;
    affected=[];
    while last_page is None or page_size*page<=7000:
        search_result=conn.search_hits(sort_direction='Descending',
                                       page_size=page_size, page_number=page);

        if last_page is None:
            total_num_results = int(search_result.TotalNumResults)
            last_page = total_num_results/page_size;

        print "Processing page %d of %d" % (page,last_page)

        
        for r in search_result:
            resp.write(str(r.HITId));
            resp.write(" ");
            resp.write(str(r.HITTypeId));
            resp.write(" ");
            resp.write(str(r.HITStatus));
            resp.write("\n");
            if r.HITStatus=='Assignable':
                if r.HITTypeId==session.hit_type:
                    affected.append(r.HITId)
                    num_affected += 1;

                    if 0==1:
                        resp.write("id:");
                        resp.write(str(r.HITId));
                        resp.write("<br/>\ntype:");
                        resp.write(str(r.HITTypeId));
                        resp.write("<br/>\n");
                        resp.write(str(r.HITStatus));
                        resp.write("<br/>\n");
                else:
                    num_skipped_by_type += 1;
            else:
                pass

            if r.HITStatus not in counts:
                counts[r.HITStatus]=0

            counts[r.HITStatus] += 1;
        page+=1

    for hID in affected:
        expire_hit(conn,hID)

    resp.write('<hr/><h2>Assignable:</h2>')
    resp.write('Affected: %d<br/>' % num_affected);
    resp.write('Skipped: %d<br/>' % num_skipped_by_type);
    resp.write('<hr/><h2>Hits by type</h2>')
    for k,v in counts.items():
        resp.write('%s  : %d<br/>' % (k,v));
        
    return resp


def get_ros_publishers(request):
    if not ros_sender:
        return HttpResponse("none")
    else:
        s=ros_sender.get_pub_string();
        return HttpResponse(s)






def stats_session_detail(request,session_code):
    session = get_object_or_404(Session,code=session_code)
    submissions=session.submittedtask_set.all().order_by('submitted');
    for s in submissions:
        s.diff=(s.submitted - s.hit.submitted).seconds;
    
    submissions=sorted(submissions,lambda a,b:a.diff-b.diff);

    return render_to_response('mturk/stats_session_details.html',
                              {'user':request.user,'session':session,'submissions':submissions});




@login_required
def create_qualification(request,session_code,qualification_name):
    session = get_object_or_404(Session,code=session_code)
    qual = get_object_or_404(MTurkQualification,name=qualification_name)
    create_qualification_internal(session,qual)

    return HttpResponse("+")

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
        
    #params['Test']=xml.sax.saxutils.escape(qual_definition.question)
    #params['Answer']=xml.sax.saxutils.escape(qual_definition.answer)
    #params['Test']=urllib.quote(qual_definition.question)
    #params['Answer']=urllib.quote(qual_definition.answer)
    params['Test']=qual_definition.question
    params['AnswerKey']=qual_definition.answer
    #data={}
    #data['Test']=urllib.quote(qual_definition.question)
    #data['Answer']=urllib.quote(qual_definition.answer)
    print params
    conn = get_mt_connection(session);

    response = conn.make_request('CreateQualificationType', params,verb='POST')
    print response.status
    resp= conn._process_response(response, [('CreateQualificationTypeResponse',QualificationType)])
    print resp
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




def create_qualifications(request):

    results=[]
    for q in MTurkQualification.objects.all():
        if q.mt_qual_id=="":
            wrk=os.path.join(settings.MTURK_WORK,"qual",str(q.id));
            if not os.path.exists(wrk):
                os.makedirs(wrk);
            fn_q=os.path.join(wrk,'workload.question');
            fn_a=os.path.join(wrk,'workload.answer');
            fn_p=os.path.join(wrk,'workload.properties');

            fQ=open(fn_q,'w')
            print >>fQ,q.qualification_def.question
            fQ.close();

            fA=open(fn_a,'w')
            print >>fA,q.qualification_def.answer
            fA.close();

            fP=open(fn_p,'w')
            print >>fP,q.qualification_def.properties
            print >>fP,"Name=",q.qualification_def.name
            fP.close();
            
            if q.is_sandbox:
                sandbox_flag='-sandbox'
            else:
                sandbox_flag=''

            cmd=os.path.join(settings.MTURK_ENV,'MT_create_qualification.sh')
            env_file=os.path.join(settings.MTURK_ENV,'env.source');
            print [cmd, env_file, wrk, sandbox_flag]
            (output,err) = Popen(cmd +" "+env_file +" " + wrk +" "+ sandbox_flag, shell=True, stdout=PIPE,executable="/bin/bash").communicate()
            print output,err
            qual_file=os.path.join(wrk,'workload.properties.success');
            fID=open(qual_file,'r')
            qual=fID.readlines()[1].strip();
            q.mt_qual_id=qual
            q.save();

        if q.qualification_def is None:
            qd_name="Built-in"
        else:
            qd_name=q.qualification_def.name
        results.append((str(q),q.mt_qual_id,q.is_sandbox,qd_name));

    return render_to_response('mturk/internal_qual_report.html',
                              {'results':results});




def get_session_context(connections,session):
    if session.code in connections:
        return connections[session.code];

    if session.sandbox:
        awshost='mechanicalturk.sandbox.amazonaws.com'
    else:
        awshost='mechanicalturk.amazonaws.com'
        
    conn = MTurkConnection(host=awshost,aws_secret_access_key=session.funding.secret_key,aws_access_key_id=session.funding.access_key)
    te=session.task_def.type.get_engine();

    ctx=(conn,te);
    connections[session.code]=ctx

    return ctx

@login_required
def reject_worker_all(request,worker_id):
    feedback=request.REQUEST['reason']
    grade_value=3;

    (grader,created)=Worker.objects.get_or_create(worker=request.user.username)

    session_ctx={};

    rejection_counts={};
    results=SubmittedTask.objects.filter(worker=worker_id).exclude(state=4).exclude(state=3);

    strAns="assignmentIdToReject\tassignmentIdToRejectComment<br/>";
    for r in results:
        if r.session.owner != request.user:
            continue

        g=ManualGradeRecord(submission=r,quality=grade_value,feedback=feedback,worker=grader)
        g.save();

        (conn,te)=get_session_context(session_ctx,r.session);
        try:
            resp = conn.reject_assignment(r.assignment_id,feedback)
            r.valid=False;
            r.state=4;
            r.final_grade=str(grade_value);
            r.save()
            te.on_deactivate(r);
            
            r.hit.state=5; # Open
            r.hit.save();
            #print resp
            strAns=strAns+'Rejected: %s\t"%s"<br/>'% (r.assignment_id,feedback)
            if r.session.code in rejection_counts:
                rejection_counts[r.session.code] = rejection_counts[r.session.code]+1
            else:
                rejection_counts[r.session.code] = 1

        except Exception,e:
            strAns=strAns+'Reject FAILED: %s\t"%s" : %s <br/>'% (r.assignment_id,feedback,str(e))

    strAns=""
    total=0;
    for (s,c) in rejection_counts.items():
        strAns+="rejected %d submissions from session %s<br/>" %( c,s )
        total+=c;
    strAns += "<hr/>rejected %d submissions total" % total
    return HttpResponse(strAns)




def opt_get_session_submissions(request,session_code):
    session = get_object_or_404(Session,code=session_code)
    resp=HttpResponse();

    workers={};
    for s in session.submittedtask_set.all():
        if s.worker in workers:
            w=workers[s.worker];
        else:
            w=Worker.objects.get(worker=s.worker,session=None);
            workers[s.worker]=w;
            
        resp.write("%d %d %d\n" % (s.id,w.id,w.utility))
    return resp


def opt_get_session_grades(request,session_code):
    session = get_object_or_404(Session,code=session_code)
    resp=HttpResponse();

    ref={};
    ref_id=ManualGradeRecord.objects.count()+100000;
    for s in session.submittedtask_set.all():
        for g in s.manualgraderecord_set.all():
            w=g.worker
            if g.reference in ref:
                r=ref[g.reference];
            else:
                if "/" in g.reference:
                    r=int(g.reference.split("/")[1])
                else:
                    r=ref_id
                    ref_id+=1;
                ref[g.reference]=r;
            resp.write("%d %d %d %d %d %d\n" % (s.id,r,
                                             g.quality,g.valid,
                                             w.id,w.utility))
    return resp


