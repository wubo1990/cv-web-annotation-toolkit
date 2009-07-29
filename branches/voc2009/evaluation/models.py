from django.db import models
from django.contrib.auth.models import User

# Create your models here.


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

    def __unicode__(self):
        return self.name



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
            (2, 'Eval-in progress'),
            (3, 'Eval done'),
            (4, 'Eval failed'),
        )        

class Submission(models.Model):
    title=models.SlugField();
    method=models.TextField();
    description=models.TextField();
    owner=models.ForeignKey(User);
    is_public=models.BooleanField(default=False);

    to_challenge=models.ForeignKey(Challenge);
    to_challenge_state=models.IntegerField(choices=CHALLENGE_STATE);

    state=models.IntegerField(choices=SUBMISSION_STATE,default=1);
    score=models.DecimalField(max_digits=5,decimal_places=4,
                              default=0.0,
                              help_text="Submission score in the challenge.");
    
    when = models.DateTimeField(auto_now_add=True);    
    def __unicode__(self):
        return str(self.owner) + "/" + self.method + "/" +self.title

    def get_scores(self):
        return submissionscores_set.order_by('category')

class SubmissionScore(models.Model):
    score=models.DecimalField(max_digits=5,decimal_places=4,
                              default=0.0,
                              help_text="Submission score in the challenge.");
    category=models.TextField();
    submission=models.ForeignKey(Submission);

class Report(models.Model):
    text=models.TextField();
    when = models.DateTimeField(auto_now_add=True);
    submission=models.ForeignKey(Submission);
