#***********************************************************
#* Software License Agreement (BSD License)
#*
#*  Copyright (c) 2008, Willow Garage, Inc.
#*  All rights reserved.
#*
#*  Redistribution and use in source and binary forms, with or without
#*  modification, are permitted provided that the following conditions
#*  are met:
#*
#*   * Redistributions of source code must retain the above copyright
#*     notice, this list of conditions and the following disclaimer.
#*   * Redistributions in binary form must reproduce the above
#*     copyright notice, this list of conditions and the following
#*     disclaimer in the documentation and/or other materials provided
#*     with the distribution.
#*   * Neither the name of the Willow Garage nor the names of its
#*     contributors may be used to endorse or promote products derived
#*     from this software without specific prior written permission.
#*
#*  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#*  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#*  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
#*  FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
#*  COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
#*  INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
#*  BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#*  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#*  CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
#*  LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
#*  ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
#*  POSSIBILITY OF SUCH DAMAGE.
#***********************************************************


# Python imports
import urllib,uuid,os,shutil,copy, math
import time
import cPickle as pickler

# Library imports
from PIL import Image
import yaml

# Django imports
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse,Http404,HttpResponseRedirect
from django.shortcuts import render_to_response,get_object_or_404 
from django.views.generic.list_detail import object_list
from django.contrib.auth.decorators import login_required
from django.views.static import serve as static_serve

# Project imports
import ros_integration

from models import *
from models_stats import *

from common import *


def index(request):
    return HttpResponse("Mechanical turk server.")


@login_required
def main(request):
    """List of user sessions"""
    if not request.user.is_anonymous():
        sessions=request.user.session_set.all().order_by('-id');
    else:
        sessions=[];
    return render_to_response('mturk/main.html',{'user':request.user,'sessions':sessions});

@login_required
def main_all(request):
    """List of all sessions
    @todo: Create a permission to see other users' sessions
    """
    sessions=Session.objects.all().order_by('-id');
    return render_to_response('mturk/main.html',{'user':request.user,'sessions':sessions});

	


	

def show_session_hits(request,session_code,hit_state,page=1):
    session = get_object_or_404(Session,code=session_code)
    if int(hit_state)>0:
        hits=session.mthit_set.filter(state=int(hit_state))
    else:
        hits=session.mthit_set.all();
    
    num_per_page=session.task_def.type.get_engine().get_internal_params().get('list_num_per_page',settings.NUM_HITS_PER_PAGE)

    page_range=map(lambda x:int(math.floor(x/num_per_page)+1),range(1,session.submittedtask_set.all().count(),num_per_page));

    nav={'session':session}
    return object_list(request,queryset=hits, paginate_by=num_per_page, page=page,
                       template_name='mturk/session_hits_list.html',extra_context={'session':session,'page_range':page_range,'nav':nav});



def post_image(request,session_code=None,frame=None):

    if session_code is None:
        session_code = request.REQUEST['session']

    if frame is None:
        frame = request.REQUEST['frame']


    image_dir=os.path.join(settings.DATASETS_ROOT,session.code);

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

    return HttpResponse(frame)


def post_video(request,session_code=None,video_file=None):

    if session_code is None:
        session_code = request.REQUEST['session']

    if video_file is None:
        video_file = request.REQUEST['video_file']

    video_dir=os.path.join(settings.DATASETS_ROOT,session.code);

    if not os.path.exists(video_dir):
        os.makedirs(video_dir);

    video=request.FILES['video']
    storage = FileSystemStorage(image_dir);
    path = storage.save(os.path.join(image_dir,video_file),video);

    return HttpResponse(video_file)








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
        nav={'session':session}
	protocol=session.task_def.type.name;
    	results=session.submittedtask_set.all()[0:10];
	
	objects=[];
	for r in results:
		annURL=r.get_persistent_url2();
		comparison_list=urllib.quote_plus(annURL)
		objects.append({'submission':r,'url':comparison_list});

	return render_to_response('protocols/' +protocol+'/show_list.html',
				{'object_list':results,'nav':nav});

def show_paged_results_base(request,session_code):
    return HttpResponseRedirect("p1/");


@login_required
def show_sessions(request):
	sessions = Session.objects.all()
	return render_to_response('show_sessions.html', {'sessions':sessions})

def show_paged_results(request,session_code,page=1,order_by=None):
	session = get_object_or_404(Session,code=session_code)
        nav={'session':session};

	protocol=session.task_def.type.name;

        if order_by:
            results=session.submittedtask_set.order_by(order_by);
        else:
            results=session.submittedtask_set.all();

        num_per_page=session.task_def.type.get_engine().get_internal_params().get('list_num_per_page',settings.NUM_HITS_PER_PAGE)

	page_range=map(lambda x:int(math.floor(x/num_per_page)+1),range(1,session.submittedtask_set.all().count(),num_per_page));

	return object_list(request,queryset=results, paginate_by=num_per_page, page=page,
			template_name='protocols/' +protocol+'/show_list.html',extra_context={'page_range':page_range,'nav':nav});

@login_required
def show_all_results(request,session_code):
        session = get_object_or_404(Session,code=session_code)
        protocol=session.task_def.type.name
        results=session.submittedtask_set.all()
        extra_context={'nav':{'session':session}}
        return object_list(request,queryset=results,template_name='protocols/'+protocol+'/grading_list.html',extra_context=extra_context);

@login_required
def show_bad_results_paged_base(request,session_code):
    return HttpResponseRedirect("p1/");

@login_required
def show_bad_results_paged(request,session_code,page=1,order_by=None,num_per_page=None,template_name=None):
    session = get_object_or_404(Session,code=session_code)

    protocol=session.task_def.type.name;

    if order_by:
        results=session.submittedtask_set.order_by(order_by);
    else:
        results=session.submittedtask_set.all();
        results=results.filter(final_grade__lt=6);


    if not num_per_page:
        num_per_page=session.task_def.type.get_engine().get_internal_params().get('list_num_per_page',settings.NUM_HITS_PER_PAGE)

    page_range=map(lambda x:int(math.floor(x/num_per_page)+1),range(1,results.count(),num_per_page));

    if not template_name:
        template_name='protocols/' +protocol+'/show_list.html'

    nav={'session':session}
    return object_list(request,queryset=results, paginate_by=num_per_page, page=page,
                    template_name=template_name,extra_context={'page_range':page_range,'nav':nav});


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
        
        nav={'session':session}
	return object_list(request,queryset=results, paginate_by=num_per_page, page=page,
			template_name=template_name,extra_context={'page_range':page_range,'nav':nav});



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

        nav={'session':session}
	return object_list(request,queryset=results, paginate_by=num_per_page, page=page,
			template_name=template_name,extra_context={'page_range':page_range,'nav':nav});



@login_required
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
        nav={'session':session}
        return object_list(request,queryset=results, paginate_by=num_per_page, page=page,
                        template_name=template_name,extra_context={'page_range':page_range,'nav':nav});






def show_most_recent_result(request,session_code,page=1):
	session = get_object_or_404(Session,code=session_code)
	protocol=session.task_def.type.name;
    	results = get_most_recent_result(session);
	print results
        if results==None:
            raise Http404;
	
        num_per_page=session.task_def.type.get_engine().get_internal_params().get('list_num_per_page',settings.NUM_HITS_PER_PAGE)

	page_range=map(lambda x:int(math.floor(x/num_per_page)+1),range(1,session.submittedtask_set.all().count(),num_per_page)); 
        
        nav={'session':session}
	return object_list(request,queryset=results, paginate_by=num_per_page, page=page,
			template_name='protocols/' +protocol+'/show_list.html',extra_context={'refresh_rate':10000,'nav':nav});

@login_required
def show_sessions(request):
	sessions = Session.objects.all()
	return render_to_response('show_sessions.html', {'sessions':sessions})

@login_required
def grading_paged_base(request,session_code):
    return HttpResponseRedirect("p1/");

@login_required
def grading_paged(request,session_code,page=1):
	session = get_object_or_404(Session,code=session_code)
	protocol=session.task_def.type.name;

    	results=session.submittedtask_set.all();

        nav={'session':session}
	return object_list(request,queryset=results, paginate_by=10, page=page,
			template_name='protocols/' +protocol+'/grading_list.html',extra_context={'nav':nav});

@login_required
def mark_as_gold_submission(request,submission_id):
    submission = get_object_or_404(SubmittedTask,id=submission_id)
    workitem = submission.hit;
    (gs,created)=GoldSubmission.objects.get_or_create(workitem=workitem,submission=submission);
    if created:
        gs.save();
    return HttpResponse("+")

@login_required
def unmark_as_gold_submission(request,submission_id):
    submission = get_object_or_404(SubmittedTask,id=submission_id)
    workitem = submission.hit;

    try:
        gs=GoldSubmission.objects.get(workitem=workitem,submission=submission);
        gs.delete()
    except:
        return HttpResponse("-")

    return HttpResponse("+")




@login_required
def grading_thumbnail_random(request,session_code):
	session = get_object_or_404(Session,code=session_code)
	protocol=session.task_def.type.name;

    	results=session.submittedtask_set.all().extra(select={'rv':'RAND()'}).order_by('rv');

        nav={'session':session}
	return object_list(request,queryset=results, paginate_by=9, page=1,
                           template_name='protocols/' +protocol+'/grading_thumbnail.html',extra_context={'nav':nav});

@login_required
def grading_by_worker_paged_base(request,session_code,worker_code):
    return HttpResponseRedirect("p1/");


@login_required
def grading_by_worker_paged(request,session_code,worker_code,page=1):
	session = get_object_or_404(Session,code=session_code)
	protocol=session.task_def.type.name;

        num_per_page=session.task_def.type.get_engine().get_internal_params().get('list_num_per_page',10)

    	results=session.submittedtask_set.all().filter(worker=worker_code);

        nav={'session':session}
	return object_list(request,queryset=results, paginate_by=num_per_page, page=page,
                           template_name='protocols/' +protocol+'/grading_list.html',extra_context={'nav':nav});

@login_required
def grading_by_worker_no_session_paged_base(request,session_code,worker_code):
    raise NotImplemented();

@login_required
def grading_by_worker_no_session_paged(request,worker_code,page=1):
    raise NotImplemented();

@login_required
def grading_by_submission_id(request,session_code,submission_id):
    session = get_object_or_404(Session,code=session_code)
    results = session.submittedtask_set.filter(id=submission_id)
    print results,session,submission_id
    protocol=session.task_def.type.name;

    return object_list(request,queryset=results, paginate_by=1, page=1,
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







@login_required
def adjudicate_by_submission_id(request,session_code,submission_id):
	session = get_object_or_404(Session,code=session_code)
	results = session.submittedtask_set.filter(id=submission_id)
        print results,session,submission_id
	protocol=session.task_def.type.name;
        nav={'session':session}
	return object_list(request,queryset=results, paginate_by=1, page=1,
                           template_name='protocols/' +protocol+'/grading_list2.html',extra_context={'nav':nav});



@login_required
def adjudicate_by_conflict_type(request,session_code,grade_A,grade_B,page=1):
	session = get_object_or_404(Session,code=session_code)

        submission_ids=get_grade_conflict_submission_list(session,grade_A,grade_B);
	results = session.submittedtask_set.filter(id__in=submission_ids)

	protocol=session.task_def.type.name;
        nav={'session':session}
	return object_list(request,queryset=results, paginate_by=10, page=page,
                           template_name='protocols/' +protocol+'/grading_list2.html',extra_context={'nav':nav});



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


@login_required
def show_grading_conflict_details(request,session_code,grade_1_id,grade_2_id):
    session = get_object_or_404(Session,code=session_code)

    results=get_grade_conflict_details(session,grade_1_id,grade_2_id)
    nav={'session':session}
    return render_to_response('mturk/conflict_details_list.html',
                              {'session':session,'g1':grade_1_id,'g2':grade_2_id,'conflicts':results,'nav':nav})


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

@login_required
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

@login_required
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
        ref_uid = request.POST.get('ref_uid','')

	params="frame="+frame+"&original_name="+original_name + \
            "&image_size=" + img_size + \
            "&frame_id=" + ref_frame + \
            "&ref_time=" + ref_time + \
            "&topic_in=" + ref_topic + \
            "&topic_out=" + topic_out +\
            "&ref_uid=" + ref_uid
        print params



        hit=MTHit(session=session,ext_hitid=rand_id,int_hitid=id,parameters=params);
	hit.save();

	if session.standalone_mode:
            return HttpResponse("%s" % hit.ext_hitid)

        created,ext_id = activate_hit(session,hit)
        if not created:
            return HttpResponse("- %s" % ext_id)

	return HttpResponse("%s" % ext_id)





def new_HIT_generic(request):
    """ 
    @param session: Session code
    @param parameters: Raw work unit parameters
    @return: Magic ID of the work unite or "- {{error message}}" if it failed to create it.
    """
    session_code = request.REQUEST['session']

    session = get_object_or_404(Session,code=session_code)

    if session.mthit_set.count()>=session.HITlimit:
            return HttpResponse("- HIT creation failed: maximum HIT count (%d) reached" % session.HITlimit)

    id = session.mthit_set.count()+1;
    rand_id=str(uuid.uuid4())+"-"+str(id)

    params = request.REQUEST['parameters']

    hit=MTHit(session=session,ext_hitid=rand_id,int_hitid=id,parameters=params);
    hit.save();

    if session.standalone_mode:
        return HttpResponse("%s" % hit.ext_hitid)

    created,ext_id = activate_hit(session,hit)
    if not created:
        return HttpResponse("- %s" % ext_id)

    return HttpResponse("%s" % ext_id)



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
        
    if "delay" in request.REQUEST:
        delay=float(request.REQUEST["delay"])
    else:
        delay=None
    print new_hit_type,old_hit_type
    (num_affected,num_failures)=update_session_hittype(session,new_hit_type,delay);
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


def update_session_hittype(session,new_hit_type,delay=None):
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
        if delay:
            time.sleep(delay)

    return (num_affected,num_failures)

@login_required
def touch_random_session_hit(request,session_code):
    session = get_object_or_404(Session,code=session_code)

    if session.standalone_mode:
        return HttpResponse("- The session is standalone. Can not update")

    (num_affected,num_failures)=internal_touch_update_random_session_hit(session);
    return HttpResponse("+ affected %d num_failures %d"%( num_affected,num_failures))

def internal_touch_update_random_session_hit(session):
    hits=session.mechturkhit_set.all(); #.filter(state=6)
    num_hits = hits.count()
    print num_hits
    if num_hits==0:
        return (0,0)
    
    selected_hit=random.randint(0,num_hits-1)
    conn = get_mt_connection(session)    
    num_failures =0;
    num_affected=0;
    h=hits[selected_hit]
    print h.mechturk_hit_id
    try:
        rs = change_hit_type(conn,h.mechturk_hit_id,session.hit_type)
        num_affected+=1;
    except MTurkException :
        num_failures+=1;

    return (num_affected,num_failures)










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
    for q in session.mturk_qualification.all():
        new_session.mturk_qualification.add(q)
    return HttpResponse("+ %d" % new_session.id)

@login_required
def submit_redo_HITs(request,session_code):
    session = get_object_or_404(Session,code=session_code);
    nav={'session':session};

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

        created,ext_id = activate_hit(session,hit)
        if not created:
            return render_to_response('mturk/error_report.html',{'error':ext_id,'session':session,'nav':nav});

        print "Hit",hit.id ,"is submitted"
        num_submitted += 1;

    if num_submitted>0:
        session.is_running=True;
        session.save()

    return render_to_response("mturk/submit_redo.html",{"num_submitted": num_submitted,'nav':nav})

def get_good_hit_results_xml(request,ext_id):
    return get_hit_results_xml(request,ext_id,True)

def get_hit_results_xml(request,ext_id,filter_good_results=False):
    task_id=ext_id;
    print task_id;

    task = get_object_or_404(MTHit,ext_hitid=task_id);
    print task

    s="";
    for st in task.submittedtask_set.all():

        print st.id,st.final_grade 

        if filter_good_results:
            if not st.valid:
                continue
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
        break

    if s=="":
        raise Http404;

    if not s.startswith("<?"):
        s="<?xml version='1.0'?><annotations>"+s+"</annotations>";
    return HttpResponse(s, mimetype="text/xml");




@login_required
def grading_submit_session(request,session_code,grading_session_code):
    session = get_object_or_404(Session,code=session_code);

    grade_all_submissions=False;
    if "grade_all_submissions" in request.REQUEST:
        grade_all_submissions=bool(request.REQUEST['grade_all_submissions'])


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

    exclude,created=SessionExclusion.objects.get_or_create(session_A=session,session_B=grading_session,decline_reason="You can't do grading, because you submitted work in this session.");
    exclude.save();

    if  request.user != session.owner and not request.user.is_superuser:
        raise Http404;


    te=grading_session.task_def.type.get_engine();
    grading_params=te.reinterpret_task_parameters(grading_session.task_def)

    if grade_all_submissions:
        submissions_rs=session.submittedtask_set.all()
    else:
        submissions_rs=session.submittedtask_set.filter(state__in=[1,2])
        

    stats={};
    stats['num_to_grade']=submissions_rs.count();
    all_grading_items=[];

    for t in submissions_rs:
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

    nav={'session':session};
    return render_to_response('mturk/submitted_for_grading.html',{'user':request.user,'session':session,'grading_session':grading_session,'stats':stats,'failed_msgs':failed_msgs,'nav':nav});


def add_hit_to_session(session,params):
    if session.mthit_set.count()>=session.HITlimit:
        return (False,"HIT creation failed: maximum HIT count (%d) reached" % session.HITlimit)

    id = session.mthit_set.count()+1;
    rand_id=str(uuid.uuid4())+"-"+str(id)
    hit=MTHit(session=session,ext_hitid=rand_id,int_hitid=id,parameters=params);
    hit.save();
    

    if session.standalone_mode:
        return (True,"%s" % hit.ext_hitid)

    return activate_hit(session,hit)








def dynamic_task(request,path):
    print path[0:-4]
    objects=Task.objects.filter(name=path[0:-4])
    if len(objects)==0:
        return static_serve( request,path=path,document_root='/var/datasets/tasks/')
    else:
        return HttpResponse(str(objects[0].interface_xml), mimetype="text/xml");








def get_session_images2(request,session_code):
    return get_session_images(request,session_code,True)

def get_session_images3(request,session_code):
	session = get_object_or_404(Session,code=session_code)

        response = HttpResponse();

	for hit in session.mthit_set.all():            
            parms=hit.parse_parameters();
            
            frame=parms.get('frame',None);
            if frame is None:
                frame=parms.get('image_url','n/a');
            frame_id=parms.get('frame_id','n/a')
            ref_time=parms.get('ref_time','n/a')
            topic_in=parms.get('topic_in','n/a')
            original_name=parms.get('original_name','n/a')

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
        task_type=session.task_def.type;
        results={};
	for hit in session.mthit_set.all():            
            parms=hit.parse_parameters();

            hit_d={};
            hit_d['task_type']=str(task_type.name);
            hit_d['task_id']=str(session.task_def.name);
            if task_type=="gxml":
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
                hit_d['image_id']=img_id;

            hit_d['int_id']=hit.id;
            hit_d['ext_work_unit_id']=hit.ext_hitid;
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











def compute_final_grade(session,result):
    grade = None
    feedback="";

    for g in result.manualgraderecord_set.all():
        if not g.valid:
            continue

        if grade:
            if grade>g.quality:
                grade=g.quality;
                feedback=g.feedback;
        else:
            grade=g.quality;
            feedback=g.feedback;

    return (grade,feedback)





def finalize_graded_submissions(session):
    results=session.submittedtask_set.all().exclude(state=4).exclude(state=3)
    
    (conn,te)=get_session_context({},session);

    num_approved=0;
    num_failed_to_approve=0;
    num_rejected=0;
    num_failed_to_reject=0;
    for r in results:

        (grade,feedback) = compute_final_grade(session,r);
        if grade is None:
            #It's not a graded submission
            continue

        feedback += get_submission_url_notice(r)

        if grade>3:
            success=mt_approve_submission(r,grade,feedback,  conn,te);
            if success:
                num_approved+=1;
            else:
                num_failed_to_approve+=1;
        else:
            success=mt_reject_submission(r,grade,feedback,  conn,te);
            if success:
                num_rejected+=1;
            else:
                num_failed_to_reject+=1;

    return ( num_approved, num_rejected, num_failed_to_approve, num_failed_to_reject)


def repost_idle_submissions(session):

    num_activated=0;
    for work_unit in session.mthit_set.filter(state__in=[1,5,7]):
        activate_hit(session,work_unit)
        num_activated+=1;
    if num_activated>0:
        session.is_running=True;
        session.save()

    return num_activated

def update_session_state(session):

    still_running=False
    for work_unit in session.mthit_set.all():
        num_required=work_unit.get_num_required_submissions();
        num_available=work_unit.submittedtask_set.filter(valid=1)
        if num_required>num_available:
            still_running=True
            break

    if still_running:
        session.is_running=True;
        session.save()


def update_submission_states(session):
    for s in session.submittedtask_set.all().filter(revision_state=1,valid=1,approval_state=1):
        shall_reject=False
        shall_approve=False
        for g in s.manualgraderecord_set.all().filter(valid=1):
            if g.quality>=5:
                shall_approve=True
            elif g.quality<5:
                shall_reject=True

        if shall_reject and shall_approve:
            s.state=7;
        elif shall_approve:
            s.state=5;
        elif shall_reject:
            s.state=6;
        else:
            s.state=8;
        s.save()
        




@login_required
def process_graded_submissions(request,session_code):
    session = get_object_or_404(Session,code=session_code)
    nav={'session':session};

    try:
        (conn,te) = get_session_context({},session)

        ( num_approved, num_rejected, num_failed_to_approve, num_failed_to_reject) = finalize_graded_submissions(session);

        if num_failed_to_approve>0 or num_failed_to_reject>0:
            return render_to_response('mturk/failure.html',
                                      {'msg':'Failed to approve %d submissions, failed to reject %d submissions. See server log for details.' % (num_failed_to_approve,num_failed_to_reject),'nav':nav})


        num_activated = repost_idle_submissions(session);


        stats={'num_activated':num_activated,'num_approved':num_approved,'num_rejected':num_rejected};
        return render_to_response('mturk/session_process_action_report.html',
                                  {'action':'Process graded submissions','stats':stats,'session':session,'nav':nav})

    except MTurkException, ex:
        return render_to_response('mturk/aws_error_report.html',{'resultset':ex.rs,'session':session,'nav':nav});





@login_required
def reject_poor_results(request,session_code):
	session = get_object_or_404(Session,code=session_code);

        if session.sandbox:
            awshost='mechanicalturk.sandbox.amazonaws.com'
        else:
            awshost='mechanicalturk.amazonaws.com'

        conn = get_mt_connection(session)    

        results=session.submittedtask_set.all().exclude(state=4).exclude(state=3);
        print results.count()
        te=session.task_def.type.get_engine();

        approval_results=[];
        errors=[];
        num_approved =0;
        num_rejected =0;
        num_skipped  =session.submittedtask_set.filter(state__in=[3,4]).count();
        num_undecided=0;
        num_errors=0;

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
                    print "Result ",r.id,"has no grades (",num_inactive," inactive)"
                    num_undecided += 1
                    continue
                else:
                    print "Result ",r.id,"has grade ",grade

		doReject=1;
		if grade>3:
			doReject=0;
		if doReject:
                    try:
                        feedback += get_submission_url_notice(r)
                        resp = conn.reject_assignment(r.assignment_id,feedback)
                        r.valid=False;
                        r.state=4;
                        r.final_grade=str(grade);
                        r.save()
                        te.on_deactivate(r);

                        r.hit.state=5; # Open
                        r.hit.save();
                        print resp
                        approval_results.append( {'result':'rejected','assignment_id':r.assignment_id,'feedback':feedback})
                        num_rejected += 1
                    except Exception,e:
                        errors.append('Reject FAILED: %s\t"%s" : %s <br/>'% (r.assignment_id,feedback,str(e)))
                        num_errors += 1;

        report={'num_approved':num_approved,
                'num_rejected':num_rejected,
                'num_skipped':num_skipped,
                'num_undecided':num_undecided,
                'num_errors':num_errors,
                'results':approval_results,
                'errors':errors}
        nav={'session':session};
	return render_to_response("mturk/approval_report.html",{'report':report,'nav':nav});


def get_submission_url_notice(r):
    return "[See your submission:"+settings.HOST_NAME_FOR_MTURK+"mt/view_submission/"+r.hit.ext_hitid+"/"+str(r.id)+"/ ]"



@login_required
def approve_good_results(request,session_code):
	session = get_object_or_404(Session,code=session_code);

        conn = get_mt_connection(session)    

     	results=session.submittedtask_set.all().exclude(state=4).exclude(state=3)
        te=session.task_def.type.get_engine();

        approval_results=[];
        errors=[];
        num_approved =0;
        num_rejected =0;
        num_skipped  =session.submittedtask_set.filter(state__in=[3,4]).count();
        num_undecided=0;
        num_errors=0;
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
                    num_undecided += 1
                    continue

		doAccept=0;
		if grade>3:
			doAccept=1;

                        
                feedback += get_submission_url_notice(r)

		if doAccept:
                    try:
                        print feedback
                        num_approved += 1;
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

                        approval_results.append( {'result':'approved','assignment_id':r.assignment_id,'feedback':feedback})
                    except Exception,e:
                        errors.append('Approve FAILED: %s\t"%s" : %s <br/>'% (r.assignment_id,feedback,str(e)))

        update_session_state(session)

        report={'num_approved':num_approved,
                'num_rejected':num_rejected,
                'num_skipped':num_skipped,
                'num_undecided':num_undecided,
                'num_errors':num_errors,
                'results':approval_results,
                'errors':errors}
        nav={'session':session};
	return render_to_response("mturk/approval_report.html",{'report':report,'nav':nav});


@login_required
def approve_all_results(request,session_code):
	session = get_object_or_404(Session,code=session_code);

        conn = get_mt_connection(session)    

     	results=session.submittedtask_set.all().exclude(state=4).exclude(state=3)
        approval_results=[];
        errors=[];
        num_approved =0;
        num_rejected =0;
        num_skipped  =session.submittedtask_set.filter(state__in=[3,4]).count();
        num_undecided=0;
        num_errors=0;
	for r in results:
            try:
                feedback="Automatic approval. " + get_submission_url_notice(r)
                resp = conn.approve_assignment(r.assignment_id,feedback)
                print resp
                r.state=3;
                r.save();
                r.hit.state=4; # Finalized
                r.hit.save();
                num_approved += 1
                approval_results.append( {'result':'approved','assignment_id':r.assignment_id,'feedback':feedback})
            except Exception,e:
                errors.append('Approve FAILED: %s\t"%s" : %s <br/>'% (r.assignment_id,feedback,str(e)))
                num_errors+=1

        update_session_state(session)

        report={'num_approved':num_approved,
                'num_rejected':num_rejected,
                'num_skipped':num_skipped,
                'num_undecided':num_undecided,
                'num_errors':num_errors,
                'results':approval_results,
                'errors':errors}
        nav={'session':session};
	return render_to_response("mturk/approval_report.html",{'report':report,'nav':nav});



@login_required
def approve_all_results_str(request,session):
    conn = get_mt_connection(session)    

    results=session.submittedtask_set.all().exclude(state=4).exclude(state=3)

    approval_results=[];
    errors=[];
    num_approved =0;
    num_rejected =0;
    num_skipped  =session.submittedtask_set.filter(state__in=[3,4]).count();
    num_undecided=0;
    num_errors=0;

    for r in results:
        try:
            feedback=get_submission_url_notice(r)            
            resp = conn.approve_assignment(r.assignment_id,feedback)
            num_approved += 1
            approval_results.append( {'result':'approved','assignment_id':r.assignment_id,'feedback':feedback})
        except Exception,e:
            errors.append('Approve FAILED: %s\t"%s" : %s <br/>'% (r.assignment_id,feedback,str(e)))
            num_errors += 1
        
    report={'num_approved':num_approved,
            'num_rejected':num_rejected,
            'num_skipped':num_skipped,
            'num_undecided':num_undecided,
            'num_errors':num_errors,
            'results':approval_results,
            'errors':errors}
    nav={'session':session};
    return render_to_response("mturk/approval_report.html",{'report':report,'nav':nav});



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





@login_required
def expire_session_hits(request,session_code):
    session = get_object_or_404(Session,code=session_code);

    conn = get_mt_connection(session)    

    hits=session.mechturkhit_set.all()
    
    num_skipped =0;
    num_affected=0;
    for h in hits:
        if h.state==1:
            expire_hit(conn,h.mechturk_hit_id)
            h.state=5
            h.save()
            num_affected+=1;
        else:
            num_skipped +=1;

    session.is_running=False;
    session.save()
    report={'num_affected':num_affected,
            'num_skipped':num_skipped}
    nav={'session':session};

    
    return render_to_response("mturk/expire_session_hits.html",{"report":report,"nav":nav})


@login_required
def expire_session_hits_by_type(request,session_code):
    session = get_object_or_404(Session,code=session_code);

    conn = get_mt_connection(session)    


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
    pub_list=ros_integration.get_publishers()
    resp=HttpResponse(yaml.dump(pub_list));
    return resp;

def get_ros_topic_publishers(request):
    topic_name=request.REQUEST['topic']
    pub_list=ros_integration.get_ros_topic_publishers(topic_name)
    resp=HttpResponse(yaml.dump(pub_list));
    return resp;






@login_required
def stats_session_detail(request,session_code):
    session = get_object_or_404(Session,code=session_code)
    nav={'session':session};

    te=session.task_def.type.get_engine();
    
    submissions=session.submittedtask_set.all().order_by('submitted');
    print submissions
    times=[];
    for s in submissions:
        times.append(te.estimate_time_spent(s));
        s.diff=(s.submitted - s.hit.submitted).seconds;
    
    submissions=sorted(submissions,lambda a,b:a.diff-b.diff);
    
    if len(times)==0:
        average_time='N/A';
    else:
        average_time="%0.2f" % (sum(times)/len(times));

    return render_to_response('mturk/stats_session_details.html',
                              {'user':request.user,'session':session,'submissions':submissions,'times':times,'average_time':average_time,'nav':nav});














def get_session_context(connections,session):
    if session.code in connections:
        return connections[session.code];

    conn = get_mt_connection(session)    

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
            feedback2=feedback+get_submission_url_notice(r)
            resp = conn.reject_assignment(r.assignment_id,feedback2)
            r.valid=False;
            r.state=4;
            r.final_grade=str(grade_value);
            r.save()
            te.on_deactivate(r);
            
            r.hit.state=5; # Open
            r.hit.save();

            strAns=strAns+'Rejected: %s\t"%s"<br/>'% (r.assignment_id,feedback2)
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




@login_required
def fix_num_required_submissions(request):
    for h in MTHit.objects.all():
        print h.id
        if h.num_required_submissions==0:
            h.num_required_submissions=h.session.task_def.max_assignments;
            h.save()



@login_required
def update_start_times(request):
    pass


def view_get_num_assignments(request,ext_hit_id):
    session=Session.objects.get(code=ext_hit_id);
    counts={};
    for w in session.mthit_set.all():
        counts[w.ext_hitid]=get_num_assignments(session,w);
    
    return HttpResponse(str(counts));
"""

    hit = get_object_or_404(MTHit,ext_hitid=ext_hit_id);
    N=get_num_assignments(hit.session,hit)
    return HttpResponse(str(N))
"""



def remove_session_from_queue(session):
    num_items_deleted=0;
    for queue_item in WorkPriorityQueueItem.objects.filter(work__session=session):
        queue_item.delete()
        num_items_deleted+=1;
    return {"num_items_deleted":num_items_deleted};


def update_session_queue_priority(session,new_priority):
    num_items_updated=0;
    num_assignments_updated=0;
    for queue_item in WorkPriorityQueueItem.objects.filter(work__session=session):
        queue_item.priority=new_priority;
        queue_item.save()
        num_items_updated+=1;
        num_assignments_updated += queue_item.assignments_left

    return {"num_items_updated":num_items_updated,"num_assignments_updated":num_assignments_updated};


def update_work_item_queue_priority(work_item,new_priority):
    num_items_updated=0;
    num_assignments_updated=0;
    for queue_item in WorkPriorityQueueItem.objects.filter(work=work_item):
        queue_item.priority=new_priority;
        queue_item.save()
        num_items_updated+=1;
        num_assignments_updated += queue_item.assignments_left

    return {"num_items_updated":num_items_updated,"num_assignments_updated":num_assignments_updated};



def put_session_to_the_queue(session,priority):
    stats={}
    num_items_posted=0;
    num_assignments_created=0;
    for hit in session.mthit_set.all():
        num_submitted=hit.submittedtask_set.filter(valid=1).count()
        num_required=hit.get_num_required_submissions()
        if num_required>num_submitted:
            queue_item=WorkPriorityQueueItem(queue=session.priority_queue,priority=priority,work=hit, assignments_left=num_required-num_submitted);
            queue_item.save()
            num_items_posted+=1;
            num_assignments_created += queue_item.assignments_left;

    stats["num_items_posted"] = num_items_posted;
    stats["num_assignments_created"] = num_assignments_created;
    return stats


def post_session_hits(session):

    hits=session.mthit_set.all();
    results=session.submittedtask_set.all();
    
    num_submitted=0;
    for hit in hits:
        num_submissions=hit.submittedtask_set.all().filter(valid=1).count();
        num_required=hit.get_num_required_submissions();
        if num_required>num_submissions:
            created,ext_id = activate_hit(session,hit)
            if not created:
                raise Exception("Error creating HIT:"+ext_id) #@TODO: add proper exception information

        print "Hit",hit.id ,"is submitted"
        num_submitted += 1;

    return {"num_submitted":num_submitted}


@login_required
def queue_session_work_units(request,session_code,priority):
    session = get_object_or_404(Session,code=session_code)
    nav={'session':session};

    stats=remove_session_from_queue(session);

    stats2=put_session_to_the_queue(session,priority);

    stats3=post_session_hits(session);

    stats.update(stats2)
    stats.update(stats3)

    session.is_running=True;
    session.save();

    return render_to_response('mturk/queue/put_session_report.html',
                              {'user':request.user,'session':session,'stats':stats,'nav':nav});

@login_required
def remove_session_from_the_queue(request,session_code):
    session = get_object_or_404(Session,code=session_code)
    nav={'session':session};

    stats=remove_session_from_queue(session);

    conn = get_mt_connection(session)    

    hits=session.mechturkhit_set.all()
    
    num_skipped =0;
    num_affected=0;
    for h in hits:
        if h.state==1:
            expire_hit(conn,h.mechturk_hit_id)
            h.state=5
            h.save()
            num_affected+=1;
        else:
            num_skipped +=1;

    stats2={'num_affected':num_affected,
            'num_skipped':num_skipped}

    stats.update(stats2)

    session.is_running=False;
    session.save();

    return render_to_response('mturk/queue/remove_session_from_queue_report.html',
                              {'user':request.user,'session':session,'stats':stats,'nav':nav});
