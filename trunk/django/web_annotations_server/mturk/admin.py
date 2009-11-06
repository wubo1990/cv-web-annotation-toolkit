from django.contrib import admin
from models import Session,SessionExclusion,FundingAccount,MTHit,SubmittedTask,Worker,Task,TaskType,MTurkQualificationDefinition,MTurkQualification


class FundingAccountAdmin(admin.ModelAdmin):
    pass	


class SessionAdmin(admin.ModelAdmin):
    list_display = ('code', 'task_def', 'funding', 'owner')
    fields = ('code', 'task_def', 'funding', 'standalone_mode', 'sandbox', 'HITlimit', 'hit_type', 'owner',
              'gold_standard_qualification',
              'mturk_qualification');


class MTHitAdmin(admin.ModelAdmin):
    list_display = ('session', 'ext_hitid', 'int_hitid', 'submitted', 'parameters')

class SubmittedTaskAdmin(admin.ModelAdmin):
    list_display = ('hit', 'session', 'worker', 'response', 'submitted')

class WorkerAdmin(admin.ModelAdmin):
    list_display = ('session', 'worker', 'utility')

class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'reward', 'max_assignments', 'duration')    

class TaskTypeAdmin(admin.ModelAdmin):
    list_display = ('id','name');

class MTQualAdmin(admin.ModelAdmin):
    list_display = ('id','name','qualification_def','comparator','value','is_sandbox');

class MTQualDefAdmin(admin.ModelAdmin):
    list_display = ('id','name');
    

class SessionExclusionAdmin(admin.ModelAdmin):
    pass	
          
admin.site.register(Session, SessionAdmin);
admin.site.register(SessionExclusion, SessionExclusionAdmin);
admin.site.register(SubmittedTask, SubmittedTaskAdmin);
admin.site.register(MTHit, MTHitAdmin);
admin.site.register(FundingAccount, FundingAccountAdmin);
admin.site.register(Worker,WorkerAdmin);
admin.site.register(Task,TaskAdmin);
admin.site.register(TaskType,TaskTypeAdmin);

admin.site.register(MTurkQualification,MTQualAdmin);
admin.site.register(MTurkQualificationDefinition,MTQualDefAdmin);

