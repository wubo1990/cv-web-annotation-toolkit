# Create your views here.

import shutil,os,sys

from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response,get_object_or_404
from django.template.loader import render_to_string
from django.core.files.storage import FileSystemStorage
from forms import UploadSubmissionForm
from models import *
from django.views.generic.simple import redirect_to
from django.forms.util import ErrorList
import datetime

from django.conf import settings

import csv, codecs, cStringIO


def main(request):
	if not request.user:
		return login_required(request);
	return render_to_response('evaluation/main.html',{'user':request.user})




def check_challenge_timeout(user,challenge):
	n_days=challenge.limit_in_N_days;
	default_allowance=challenge.limit_to_N_submissions;
	extra_allowance = 0
	today = datetime.date.today();
	today_minus_N=today - datetime.timedelta(days=n_days);

	for ex in SubmissionExceptions.objects.filter(for_user=user,
						      start_on__lte=today,
						      end_at__gte=today,
						      to_challenge=challenge):
	  extra_allowance += ex.allow_N_extra_submissions;

	used_allowance = Submission.objects.filter(owner=user,
					    when__gte=today_minus_N,
					    to_challenge=challenge,
					    state__in=[2,3,5,100]).count()

	can_submit=used_allowance<default_allowance + extra_allowance

	return (can_submit, used_allowance);

@login_required
def upload_submission(request):
	#if not request.user.has_perm('datastore.evaluation.add'):
	#	return render_to_response('registration/not_authorized.html')


	if request.method == 'POST':
		form = UploadSubmissionForm(request.POST, request.FILES)
		if form.is_valid():
			challenge=form.cleaned_data['challenge']
			(can_submit,past_count)=check_challenge_timeout(request.user,challenge)
			if can_submit:
				uploaded_file=request.FILES['submission_file'];
				return do_upload_submission(request,form,uploaded_file);
			else:
				form._errors['challenge']=ErrorList(["You have %d submissions to %s in past %d days. You are not allowed to submit right now. Contact the organizers if you feel this is a mistake" %(past_count,challenge.name,challenge.limit_in_N_days)]);
			#return HttpResponseRedirect('/datastore/')
	else:
		form = UploadSubmissionForm()

	challenges_info=Challenge.objects.all()
	for c in challenges_info:
		can_submit,used_allowance = check_challenge_timeout(request.user,c);
		c.can_submit=can_submit
		c.used_allowance=used_allowance

	return render_to_response('evaluation/upload_submission.html', {'form': form,'user':request.user,'challenges_info':challenges_info})






def do_upload_submission(request,form,uploaded_file):
	
	user = request.user;
        print form.cleaned_data
        challenge=form.cleaned_data['challenge']
	#challenge = get_object_or_404(Challenge,name=challenge_name);

	submission=Submission(title=form.cleaned_data['title'],
			      method=form.cleaned_data['method'],
                              description=form.cleaned_data['description'],
                              contact_person=form.cleaned_data['contact_person'],
                              affiliation=form.cleaned_data['affiliation'],
                              contributors=form.cleaned_data['contributors'],
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
	try:
		os.system(cmd)

		if os.path.exists(report_filename+'.error'):
			submission.state = 4
			notify_on_submission_failure(submission, "format check produced an error");

		elif os.path.exists(report_filename+'.final_score'):
			try:
				score=open(report_filename+'.final_score','r').readlines()[0];
				submission.score=score;
				submission.state = 3
			except:
				submission.state = 4                            
				notify_on_submission_failure(submission, "exception when reading the score");
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
	except:
		rpt=Report(text="ERROR: failed to check submission.",submission=submission);
		rpt.save();
		submission.state = 4                            
		submission.save()
		notify_on_submission_failure(submission, "exception when running format check");

	
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
        objects = request.user.submission_set.all()

    objects=objects.extra(
	    select={
		    'most_recent': 'SELECT max(s2.when) as most_recent FROM evaluation_submission s2 WHERE s2.owner_id=evaluation_submission.owner_id and s2.method=evaluation_submission.method and s2.to_challenge_id=evaluation_submission.to_challenge_id'
		    },
	    );        

    #objects=objects.

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
	objects=objects.extra(
		select={
			'most_recent': 'SELECT max(s2.when) as most_recent FROM evaluation_submission s2 WHERE s2.owner_id=evaluation_submission.owner_id and s2.method=evaluation_submission.method and s2.to_challenge_id=evaluation_submission.to_challenge_id'
			},
		);        		
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




def show_submission_public(request,submission_id):
    submission = get_object_or_404(Submission,id=submission_id);
    return render_to_response('evaluation/submission_public.html',
			      {'submission':submission})


def competition_results(request,challenge_name,competition_name):
	challenge = get_object_or_404(Challenge,name=challenge_name);	
	submissions=Submission.objects.filter(to_challenge=challenge,state=5).all();
	relevant_submissions=[];
	relevant_submission_scores=[];
	all_scores={};
	all_categories={};
	best_scores={};
	for s in submissions:
		scores=s.submissionscore_set.filter(competition=competition_name).all();
		if len(scores)==0:
			continue
		relevant_submissions.append(s);
		for one_score in scores:
			if one_score.category != one_score.competition:
				all_categories[one_score.category]=1;
			all_scores[(s.id,one_score.category)]=one_score.score;
			best_score=best_scores.get(one_score.category,-1);
			if one_score.score>best_score:
				best_scores[one_score.category]=one_score.score

	
	all_categories=all_categories.keys()
	all_categories.sort()

	for s in relevant_submissions:
		scores=[]
		n_wins=0;
		for c in all_categories:
			sv=all_scores.get( (s.id,c),0);
			if sv==best_scores[c]:
				is_winner=1;
			else:
				is_winner=0;
			scores.append((sv,is_winner));
			n_wins += is_winner;

		relevant_submission_scores.append({'submission':s,'scores':scores,'n_wins':n_wins});
	print relevant_submission_scores
	return render_to_response('evaluation/competition_results.html',
				  {'relevant_submissions':relevant_submissions,'categories':all_categories,'scores':relevant_submission_scores,'competition':competition_name});


def registration_callback(user):
	print "REG CALLBACK"
	notify_on_registration(user);



@login_required
def grant_extra_submissions(request,user_id,challenge_name):
	if not request.user.is_superuser:
		raise Http404();
	
	user = get_object_or_404(User,username=user_id);
	challenge = get_object_or_404(Challenge,name=challenge_name);

	today = datetime.date.today();

	today_plus_N=today + datetime.timedelta(days=6);

	ex=SubmissionExceptions(for_user=user,
				start_on=today,
				end_at=today_plus_N,
				to_challenge=challenge,
				allow_N_extra_submissions=2)
	ex.save()
	return HttpResponse("Done");




class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


@login_required
def get_submissions_report(request):
    if not request.user.is_superuser:
	    raise Http404();

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(mimetype='text/csv')

    response['Content-Disposition'] = 'attachment; filename=somefilename.csv'

    writer = UnicodeWriter(response)

    column_headers=["SubmissionID","Name","Method","Contact Information",
    "Affiliation","Contributors","Description","Owner id",
    "Os public","Challenge id","Challenge state","Submission state","Score","Submission time","Challenge","Owner email"];

    writer.writerow(column_headers);


    #try:
    cursor=get_results_table();
    for r in cursor.fetchall():
	    writer.writerow([unicode(s) for s in r])
    #except:
    return response
