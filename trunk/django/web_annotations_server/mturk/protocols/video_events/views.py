# Create your views here.

import shutil,os,sys

from django.http import Http404,HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response,get_object_or_404
from django.core.files.storage import FileSystemStorage
from forms import UploadVideoForm
from django.views.generic.simple import redirect_to
from django.conf import settings
import uuid

import mturk.models
import mturk.views


@login_required
def upload_video(request,session_code):
	session = get_object_or_404(mturk.models.Session,code=session_code)
	#if not request.user.has_perm('datastore.evaluation.add'):
	#	return render_to_response('registration/not_authorized.html')


	if request.method == 'POST':
		form = UploadVideoForm(request.POST, request.FILES)
		if form.is_valid():
			uploaded_file=request.FILES['video_file'];
			return do_upload_video(request,session,form,uploaded_file);
	else:
		form = UploadVideoForm()
	return render_to_response('protocols/video_events/upload_video.html', {'form': form,'user':request.user})







def do_upload_video(request,session,form,uploaded_file):
	
	user = request.user;
        print form.cleaned_data
	print uploaded_file
        submission_rt=os.path.join(settings.DATASETS_ROOT,session.code);

        id = session.mthit_set.count()+1;
	rand_id=str(uuid.uuid4())+"-"+str(id)
	print dir(uploaded_file)
	original_name =uploaded_file.name
        storage = FileSystemStorage(submission_rt);
        fname=storage.save(os.path.join(submission_rt,rand_id+".flv"),uploaded_file);

	params="video=/frames/"+session.code+"/"+rand_id+".flv&original_name="+original_name 
	print params
        hit=mturk.models.MTHit(session=session,ext_hitid=rand_id,int_hitid=id,parameters=params);
	hit.save();
	if form.cleaned_data["submit_for_annotation"]:
		(activated,id)=mturk.views.activate_hit(session,hit);
	else:
		activated=False

	return HttpResponse("done. Activated %d" % activated)
        #challenge=form.cleaned_data['challenge']
	#challenge = get_object_or_404(Challenge,name=challenge_name);
	"""
	submission=Submission(title=form.cleaned_data['title'],
			      method=form.cleaned_data['method'],
                              description=form.cleaned_data['description'],
                              owner=request.user,
                              to_challenge = challenge,
                              to_challenge_state=challenge.state,
                              state=1,
                              score=0);
	submission.save();
        submission_rt=os.path.join(challenge.data_root,'submissions/%d/' % submission.id);
        os.makedirs(submission_rt);

        submission_input_rt=os.path.join(submission_rt,'input');
        os.makedirs(submission_input_rt)

        storage = FileSystemStorage(submission_input_rt);
        fname=storage.save(None,uploaded_file);
        submission_file=os.path.join(submission_input_rt,fname)
        report_filename=os.path.join(submission_rt,'report.txt');
	if submission_file.find(' ') >-1 or submission_file.find("'")>-1 or submission_file.find('"')>-1:
		needToFixFilename=True
	else:
		needToFixFilename=False

	if needToFixFilename:
		rpt=Report(text="WARNING: space or quote found in the submission file name. Please avoid spaces and quotes in submission file name",submission=submission);
		rpt.save();
		fixed_filename=submission_file.replace(' ','_').replace("'","_").replace('"','_');
		shutil.move(submission_file,fixed_filename);
		submission_file=fixed_filename;

	submission_metadata_file=os.path.join(submission_rt,'info.txt')	
	fMeta=open(submission_metadata_file,'w');
	print >>fMeta,"id\t%d" % submission.id
	print >>fMeta,"challenge\t%s" % challenge.name
	print >>fMeta,"challenge_id\t%d" % challenge.id
	print >>fMeta,"user\t%s" % request.user.username
	print >>fMeta,"user_id\t%s" % request.user.id
	print >>fMeta,"method\t%s" % submission.method
	print >>fMeta,"submitted\t%s" % submission.when
	print >>fMeta,"submission_file\t%s" % submission_file
	fMeta.close();

        cmd="%s --submission='%s' --work_root='%s' --report='%s' --dataset_root='%s'" %(
            challenge.evaluation_engine,
            submission_file,
            submission_input_rt,
            report_filename,
            challenge.data_root)
        os.system(cmd)
        if os.path.exists(report_filename+'.error'):
            submission.state = 4
        elif os.path.exists(report_filename+'.final_score'):
            try:
                score=open(report_filename+'.final_score','r').readlines()[0];
                submission.score=score;
                submission.state = 3
            except:
                submission.state = 4                            
        else:
            submission.state = 2
            
        submission.save()

        if submission.state==3:
            category_scores_file=open(report_filename+'.score','r')
            for s in category_scores_file.readlines():
                score_parts=s.strip().split(' ');
                score=score_parts[0];
                category=score_parts[1];
                ss=SubmissionScore(score=score,category=category,
                                   submission=submission);
                ss.save();

	
        return redirect_to(request,"/eval/view_submission/%d/" % (submission.id),permanent=False);                
	"""

