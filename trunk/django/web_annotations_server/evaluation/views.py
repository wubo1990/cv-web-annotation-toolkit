# Create your views here.

import shutil,os,sys

from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response,get_object_or_404
from django.core.files.storage import FileSystemStorage
from forms import UploadSubmissionForm
from models import *
from django.views.generic.simple import redirect_to


def main(request):
	if not request.user:
		return login_required(request);
	return render_to_response('evaluation/main.html',{'user':request.user})



@login_required
def upload_submission(request):
	#if not request.user.has_perm('datastore.evaluation.add'):
	#	return render_to_response('registration/not_authorized.html')


	if request.method == 'POST':
		form = UploadSubmissionForm(request.POST, request.FILES)
		if form.is_valid():
			uploaded_file=request.FILES['submission_file'];
			return do_upload_submission(request,form,uploaded_file);
			#return HttpResponseRedirect('/datastore/')
	else:
		form = UploadSubmissionForm()
	return render_to_response('evaluation/upload_submission.html', {'form': form,'user':request.user})







def do_upload_submission(request,form,uploaded_file):
	
	user = request.user;
        print form.cleaned_data
        challenge=form.cleaned_data['challenge']
	#challenge = get_object_or_404(Challenge,name=challenge_name);

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



def show_all_results(request,challenge_name):
    challenge = get_object_or_404(Challenge,name=challenge_name);
    objects = get_all_submissions(challenge);
    return render_to_response('evaluation/results_table.html',
                              {'challenge':challenge,'objects':objects});


def show_best_results(request,challenge_name):
    challenge = get_object_or_404(Challenge,name=challenge_name);
    objects = get_best_submissions(challenge);
    return render_to_response('evaluation/results_table.html',
                              {'challenge':challenge,'objects':objects});

@login_required
def show_my_submissions(request,challenge_name=None):
    if challenge_name:
        challenge = get_object_or_404(Challenge,name=challenge_name);
        objects = request.user.submission_set.filter(to_challenge=challenge);
    else:
        challenge = None
        objects = request.user.submission_set.all();        
    
    return render_to_response('evaluation/my_submissions.html',
			      {'challenge':challenge,'objects':objects,'user':request.user});


@login_required
def show_all_submissions(request,challenge_name=None):
	if not request.user.is_staff:
		raise Http404;	

	if challenge_name:
		challenge = get_object_or_404(Challenge,name=challenge_name);
		objects = Submission.objects.filter(to_challenge=challenge);
	else:
		challenge = None
		objects = Submission.objects.all();        
		
	return render_to_response('evaluation/all_submissions.html',
				  {'challenge':challenge,'objects':objects,'user':request.user});


@login_required
def show_submission(request,submission_id):
    submission = get_object_or_404(Submission,id=submission_id);
    if not submission.is_public and request.user.id != submission.owner.id:
	    if not request.user.is_staff:
		    raise Http404;

    submission_rt=os.path.join(submission.to_challenge.data_root,'submissions/%d/' % submission.id);
    submission_input_rt=os.path.join(submission_rt,'input');
    report_filename=os.path.join(submission_rt,'report.txt');
    errors_report_filename=os.path.join(submission_rt,'report.txt.error');
    if os.path.exists(report_filename):
        rpt=open(report_filename,'r');
    else:
        rpt=None
    if os.path.exists(errors_report_filename):
        err_rpt=open(errors_report_filename,'r');
    else:
        err_rpt=None

	
    messages=submission.report_set.all();
    print messages
    return render_to_response('evaluation/submission.html',
			      {'submission':submission,'rpt':rpt,'err_rpt':err_rpt,'user':request.user,'submission_messages':messages});
