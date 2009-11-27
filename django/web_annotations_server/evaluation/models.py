from django.db import models
from django.contrib.auth.models import User
from django.core.mail import send_mail,mail_admins,mail_managers
from django.template.loader import render_to_string
# Create your models here.

import os

CHALLENGE_STATE = (
            (1, 'Hidden'),
            (2, 'Development'),
            (3, 'Submission'),
            (4, 'Closed'),
            (5, 'Post-challenge'),
        )
    

    
class Challenge(models.Model):
    name=models.SlugField();
    description=models.TextField(blank=True);
    official_rules=models.URLField();

    state=models.IntegerField(choices=CHALLENGE_STATE,default=1);
    is_open=models.BooleanField(default=False);
    is_score_visible=models.BooleanField(default=False);
    
    data_root=models.TextField();
    evaluation_engine=models.TextField();

    limit_in_N_days=models.IntegerField(default=7);
    limit_to_N_submissions=models.IntegerField(default=2);

    def __unicode__(self):
        return self.name

    class Meta:
        permissions = (
            ("is_blind", "Can NOT see evaluation results"),
        )


class SubmissionExceptions(models.Model):
    for_user=models.ForeignKey(User);
    start_on = models.DateTimeField();    
    end_at = models.DateTimeField();
    allow_N_extra_submissions=models.IntegerField(default=1);
    to_challenge=models.ForeignKey(Challenge);

    def __unicode__(self):
        return "%d for %s between %s and %s to %s" %(self.allow_N_extra_submissions,
                                                     self.for_user.username,
                                                     str(self.start_on),
                                                     str(self.end_at),
                                                     str(self.to_challenge))
                                               

def get_all_submissions(challenge):
    return challenge.submission_set.all().order_by('-score')

def get_best_submissions(challenge):
    result=[];
    participants_done={};
    for r in challenge.submission_set.all().order_by('-score'):
        if r.owner.id in participants_done:
            continue
        participants_done[r.owner.id]=1;
        result.append(r);
    return result

    
SUBMISSION_STATE = (
            (1, 'New'),
            (2, 'Evaluation in progress'),
            (3, 'Evaluation completed successfully'),
            (4, 'Evaluation failed'),
            (5, 'In competition'),
            (100, 'Overriden'),
            (101, 'Hidden'),
            (102, 'Disabled'),

        )        

class Submission(models.Model):
    title=models.TextField();
    method=models.TextField();
    contact_person=models.TextField();
    affiliation=models.TextField();
    contributors=models.TextField();

    description=models.TextField();



    owner=models.ForeignKey(User);
    is_public=models.BooleanField(default=False);

    to_challenge=models.ForeignKey(Challenge);
    to_challenge_state=models.IntegerField(choices=CHALLENGE_STATE);

    state=models.IntegerField(choices=SUBMISSION_STATE,default=1);
    score=models.DecimalField(max_digits=15,decimal_places=5,
                              default=0.0,
                              help_text="Submission score in the challenge.");
    
    when = models.DateTimeField(auto_now_add=True);    
    def __unicode__(self):
        return str(self.owner) + "/" + self.method + "/" +self.title

    def get_scores(self):
        return submissionscores_set.order_by('category')

    def detailed_scores_from_files(self):
        submission_rt=os.path.join(self.to_challenge.data_root,'submissions/%d/' % self.id);
        files=os.listdir(submission_rt);
        score_files=filter(lambda s:s.startswith('comp') and s.endswith('.score'),files);
        print files,score_files
        scores=[];
        def read_scores_file(submission_rt,fn):
            file_scores=[];
            fSubmission = open(os.path.join(submission_rt,fn),'r');
            file_tag=fn.split('_')[0];
            for ln in fSubmission.readlines():
                print fn,ln
                (score,category)=ln.strip().split(' ');
                file_scores.append({'competition':file_tag,'score':score,'category':category});
            return file_scores;
        
        for fn in score_files:
            scores.extend(read_scores_file(submission_rt,fn));

        return scores;

class SubmissionScore(models.Model):
    score=models.DecimalField(max_digits=15,decimal_places=5,
                              default=0.0,
                              help_text="Submission score in the challenge.");
    competition=models.TextField();
    category=models.TextField();
    submission=models.ForeignKey(Submission);

class Report(models.Model):
    text=models.TextField();
    when = models.DateTimeField(auto_now_add=True);
    submission=models.ForeignKey(Submission);



def notify_on_submission_failure(submission, failure_context):
    print "NOTIFY ON FAILURE"
    mail_admins('Submission failed: %s ' % failure_context, 
                render_to_string('evaluation/failure_notification.txt',{'submission':submission,'failure_context':failure_context}),
                fail_silently=False);


def notify_on_registration(user):
    print "NOTIFY ON REGISTRATION"
    mail_managers('User registered: %s ' % (user.username),
                render_to_string('evaluation/user_registered.txt',{'user':user}),
                fail_silently=False);


def get_results_table():
    from django.db import connection
    cursor = connection.cursor()
    try:
        cursor.execute("""
    SELECT s.*, c.name, u.email 
    FROM `evaluation_submission` s, evaluation_challenge c, auth_user u 
    WHERE s.to_challenge_id = c.id 
      and u.id = s.owner_id
""")
	return cursor;
    except:
	return None


