from django.contrib import admin
from models import Session,SessionExclusion,FundingAccount,MTHit,SubmittedTask,Worker,Task,TaskType,MTurkQualificationDefinition,MTurkQualification,Payment,WorkerProfile,Worker,WorkerMetricsQualifications,GoldSubmission,GoldStandardQualification,WorkerTrainingProgress

from django import forms
import views
import mturk.payments.views
import mturk.qualifications.views


from lxml import etree
import string
import os.path

class FundingAccountAdmin(admin.ModelAdmin):
    pass	


class SessionAdmin(admin.ModelAdmin):
    list_display = ('code', 'task_def', 'funding', 'owner')
    fieldsets = (
        (None, {
            'fields': ('code', 'task_def', 'funding','sandbox', 'HITlimit','owner')
        }),
        ('Queue', {
            'classes': ('collapse',),
            'fields': ('use_task_priority', 'priority_queue')
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('standalone_mode', 'is_gold','gold_standard_qualification',  'mturk_qualification', 'hit_type','is_running', 'num_required_submissions' )
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
    


class MTQualForm(forms.ModelForm):
    class Meta:
        model = MTurkQualificationDefinition


    def xsd_file(self,fn):
        moddir = os.path.dirname(__file__)
        return os.path.join(moddir, 'schema', fn)
        

    def clean_question(self):
        # do something that validates your data

        question_xsd = etree.parse(self.xsd_file("QuestionForm.xsd"))
        question_schema = etree.XMLSchema(question_xsd)

        try:
            doc = etree.fromstring(self.cleaned_data["question"])
        except Exception,e:
            raise forms.ValidationError(str(e))

        if not question_schema.validate(doc):
            
            msg=string.join(
                map(lambda e:str(e),question_schema.error_log.filter_from_errors()),
                "<br/>")
            raise forms.ValidationError(msg)

        return self.cleaned_data["question"]

    def clean_answer(self):
        # do something that validates your data
        answer_xsd = etree.parse(self.xsd_file("AnswerKey.xsd"))
        answer_schema = etree.XMLSchema(answer_xsd)

        try:
            doc = etree.fromstring(self.cleaned_data["answer"])
        except Exception,e:
            raise forms.ValidationError(str(e))
        answer_schema.validate(doc)
        if not answer_schema.validate(doc):
            
            msg=string.join(
                map(lambda e:str(e),answer_schema.error_log.filter_from_errors()),
                "<br/>")
            raise forms.ValidationError(msg)

        return self.cleaned_data["answer"]

    def clean_properties(self):
        dta=self.cleaned_data["properties"]
        try:
            for s in dta.split('\n'):
                if s.strip()=="":
                    continue
                parts=s.strip().split("=")
                if len(parts)!=2:
                    raise forms.ValidationError("Error: expected key=value, got: %s"%s)
        except forms.ValidationError:
            raise                        
        except Exception,e:
            return forms.ValidationError(str(e));
        return self.cleaned_data["properties"]

class MTQualDefAdmin(admin.ModelAdmin):
    list_display = ('id','name');
    save_as=True
    form = MTQualForm




class GoldSubmissionAdmin(admin.ModelAdmin):
    pass	
class GoldQualificationAdmin(admin.ModelAdmin):
    pass	
class WorkerTrainingProgressAdmin(admin.ModelAdmin):
    pass

class SessionExclusionAdmin(admin.ModelAdmin):
    pass	

class WorkerProfileAdmin(admin.ModelAdmin):
    pass	

class WorkerMetricsQualificationsAdmin(admin.ModelAdmin):
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

admin.site.register(WorkerProfile,WorkerProfileAdmin);
admin.site.register(WorkerMetricsQualifications,WorkerMetricsQualificationsAdmin);

admin.site.register(GoldSubmission,GoldSubmissionAdmin);
admin.site.register(GoldStandardQualification,GoldQualificationAdmin);
admin.site.register(WorkerTrainingProgress,WorkerTrainingProgressAdmin);

