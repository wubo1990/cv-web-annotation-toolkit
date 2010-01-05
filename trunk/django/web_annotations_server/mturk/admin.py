from django.contrib import admin
from models import Session,SessionExclusion,FundingAccount,MTHit,SubmittedTask,Worker,Task,TaskType,MTurkQualificationDefinition,MTurkQualification,Payment

import views
import mturk.payments.views
import mturk.qualifications.views

class FundingAccountAdmin(admin.ModelAdmin):
    pass	


class SessionAdmin(admin.ModelAdmin):
    list_display = ('code', 'task_def', 'funding', 'owner')
    fieldsets = (
        (None, {
            'fields': ('code', 'task_def', 'funding','sandbox', 'HITlimit','owner')
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('standalone_mode', 'gold_standard_qualification',  'mturk_qualification', 'hit_type' )
        }),
    )
    filter_horizontal = ['mturk_qualification'];
    save_as=True




class MTHitAdmin(admin.ModelAdmin):
    list_display = ('session', 'ext_hitid', 'int_hitid', 'submitted', 'parameters')

class SubmittedTaskAdmin(admin.ModelAdmin):
    list_display = ('hit', 'session', 'worker', 'response', 'submitted')

class WorkerAdmin(admin.ModelAdmin):
    list_display = ('session', 'worker', 'utility')

class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'reward', 'max_assignments', 'duration')    
    
    save_as=True

class TaskTypeAdmin(admin.ModelAdmin):
    list_display = ('id','name');

class MTQualAdmin(admin.ModelAdmin):
    list_display = ('id','name','qualification_def','comparator','value','is_sandbox');
    save_as=True


def check_qualification(modeladmin, request, queryset):
    return mturk.qualifications.views.check_qualifications(request,queryset);
    

class MTQualDefAdmin(admin.ModelAdmin):
    list_display = ('id','name');
    save_as=True    


class SessionExclusionAdmin(admin.ModelAdmin):
    pass	


def confirm_for_payment(modeladmin, request, queryset):
    queryset.filter(state__in=[1,2]).update(state=3)
confirm_for_payment.short_description = "Confirm the payments"

def mark_for_payment(modeladmin, request, queryset):
    queryset.update(state=3)
mark_for_payment.short_description = "Mark for payments"

def make_payments(modeladmin, request, queryset):
    return mturk.payments.views.make_payments(request,queryset);
    
make_payments.short_description = "Make payments on confirmed actions"


class PaymentAdmin(admin.ModelAdmin):
    raw_id_fields = ['work_product'];
    list_filter = ['state'];
    actions = [confirm_for_payment,mark_for_payment,make_payments]
          
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

admin.site.register(Payment,PaymentAdmin);
