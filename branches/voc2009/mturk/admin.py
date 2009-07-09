from django.contrib import admin
from models import Session,FundingAccount,MTHit,SubmittedTask,Worker,Task


class FundingAccountAdmin(admin.ModelAdmin):
    pass	


class SessionAdmin(admin.ModelAdmin):
    list_display = ('code', 'task_def', 'funding', 'owner')
    fields = ('code', 'task_def', 'funding', 'standalone_mode', 'sandbox', 'HITlimit');


class MTHitAdmin(admin.ModelAdmin):
    list_display = ('session', 'ext_hitid', 'int_hitid', 'submitted', 'parameters')

class SubmittedTaskAdmin(admin.ModelAdmin):
    list_display = ('hit', 'session', 'worker', 'response', 'submitted')

class WorkerAdmin(admin.ModelAdmin):
    list_display = ('session', 'worker', 'utility')

class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'reward', 'max_assignments', 'duration')    
    


          
admin.site.register(Session, SessionAdmin);
admin.site.register(SubmittedTask, SubmittedTaskAdmin);
admin.site.register(MTHit, MTHitAdmin);
admin.site.register(FundingAccount, FundingAccountAdmin);
admin.site.register(Worker,WorkerAdmin);
admin.site.register(Task,TaskAdmin);

