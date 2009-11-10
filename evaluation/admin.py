from django.contrib import admin
from models import Challenge,Submission,SubmissionScore,SubmissionExceptions


class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('name', 'state')

class SubmissionExceptionsAdmin(admin.ModelAdmin):
    list_display = ('to_challenge','for_user', 'allow_N_extra_submissions','start_on','end_at')

class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('title', 'method', 'owner', 'score')

class SubmissionScoreAdmin(admin.ModelAdmin):
    list_display = ('id','submission','category', 'score')    
          
admin.site.register(Challenge, ChallengeAdmin);
admin.site.register(SubmissionExceptions, SubmissionExceptionsAdmin);
admin.site.register(Submission, SubmissionAdmin);
admin.site.register(SubmissionScore, SubmissionScoreAdmin);
