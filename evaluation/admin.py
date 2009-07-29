from django.contrib import admin
from models import Challenge,Submission,SubmissionScore


class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('name', 'state')

class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('title', 'method', 'owner', 'score')

class SubmissionScoreAdmin(admin.ModelAdmin):
    list_display = ('id','submission','category', 'score')    
          
admin.site.register(Challenge, ChallengeAdmin);
admin.site.register(Submission, SubmissionAdmin);
admin.site.register(SubmissionScore, SubmissionScoreAdmin);
