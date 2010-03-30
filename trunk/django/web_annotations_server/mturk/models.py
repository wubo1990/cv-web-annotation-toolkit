#License BSD
#Author Alexander Sorokin, sorokin@willowgarage.com, syrnick@gmail.com


#Python imports
import random,math,urllib,os,sys
from xml.dom import minidom

import cPickle as pickler


#Django imports

from django.conf import settings
from django.db import models,connection

from django.contrib import admin
from django.contrib.auth.models import User

from django.contrib.localflavor.us.models import USStateField


#DEPRECATED: Should remove
from django.shortcuts import get_object_or_404 

import snippets.country_field




class FundingAccount(models.Model):
	name=models.SlugField();
	access_key=models.CharField(max_length=25)
	secret_key=models.CharField(max_length=100);

	def __str__(self):
        	return self.name

task_engines={};

class TaskType(models.Model):
	name=models.SlugField();
	
	def get_engine(self):
		if self.name not in task_engines:
			m_name="mturk.protocols."+self.name
			try:
				m=__import__(m_name);
				task_engines[self.name]=m.protocols.__dict__[self.name].get_task_engine();
			except Exception,e :
				print "Can't import %s:" % m_name,e
			print task_engines
		return task_engines.get(self.name,None)

	def __unicode__(self):
		return self.name;


class Task(models.Model):
	name=models.SlugField();
	type=models.ForeignKey(TaskType);	
	
	interface_xml=models.TextField(help_text="XML describing the flash interface.");	

	instructions_url=models.URLField(help_text="url to access the instructions for this task.");	
	
	title=models.CharField(max_length=200);
	description=models.TextField();
	keywords=models.CharField(max_length=200, help_text="comma separated set of keywords describing this task");
	reward=models.DecimalField(max_digits=5,decimal_places=2,
                                 default=0.01,
                                 help_text="amount of money to reward the user (in dollars) like 0.01.");
	max_assignments=models.IntegerField(default=1,
                                            help_text="number of assignments (should be 1 or greater.)") 
        # =assignments

	duration=models.IntegerField(default=30*60,
                                     help_text="Amount of time in seconds to allow for this task to be completed.")       
        # assignmentduration

	lifetime=models.IntegerField(default=1*24*3600,
                                     help_text="Amount of time (in seconds) for the lifetime of the task.")

        # hitlifetime
	approval_delay=models.IntegerField(default=14*24*3600,
                                           help_text="Amount of time in seconds before automatic approval.")
        # =autoapprovaldelay


	def __str__(self):
        	return self.name

	
	def get_keywords(self):
		return self.keywords.split(',');


	parsed_parameters=None;

	def parse_parameters_xml(self):
		if self.parsed_parameters is not None:
			return self.parsed_parameters;
		if self.interface_xml.startswith("<?xml"):
			xmldoc = minidom.parseString(self.interface_xml);
			self.parsed_parameters=xmldoc
		
		return self.parsed_parameters;


#Not used really
SESSION_STATE = (
            (1, 'Active'),
            (2, 'HasAllTasks'),
            (3, 'HasAllSubmissions'),
            (4, 'HasAllGrades'),
            (5, 'Finalized'),
        )        
class Session(models.Model):
	code=models.SlugField(help_text="Unique session id");  
	task_def=models.ForeignKey(Task);
	funding=models.ForeignKey(FundingAccount);

	standalone_mode = models.BooleanField(default=False);
	sandbox         = models.BooleanField(default=True);
	is_gold         = models.BooleanField(default=False);

	use_task_priority = models.BooleanField(default=False);
	priority_queue = models.SlugField(default="");

	HITlimit        = models.IntegerField(default=100);

	parameters=models.TextField(null=True, blank=True); #depreciated

        owner=models.ForeignKey(User, null=True, blank=True)

	hit_type=models.CharField(max_length=100,
                                  blank=True,
				  default="",
                                  help_text="mechanical turk's id");

	state=models.IntegerField(choices=SESSION_STATE,default=1);

	is_running      = models.BooleanField(default=False);
	
	gold_standard_qualification = models.ForeignKey('GoldStandardQualification',null=True,blank=True);
	mturk_qualification = models.ManyToManyField('MTurkQualification',blank=True,null=True);
	num_required_submissions=models.IntegerField(default=0);

	class Meta:
		permissions = (
			("rpc-access", "Allow access over RPC"),
			)

	def parse_parameters(self):
		return {};
	
	def __str__(self):
        	return self.code

	def get_num_required_submissions_per_item(self):
            if self.num_required_submissions==0:
		return self.task_def.max_assignments
	    else:
                return self.num_required_submissions

	def num_open_submissions(self):
		return self.submittedtask_set.exclude(state=3).exclude(state=4).count();
	def num_submissions(self):
		return self.submittedtask_set.count();

	def list_downloads(self):
		res={};
		download_rt=os.path.join(settings.DATASETS_ROOT,'downloads',self.code)
		if not os.path.exists(download_rt):
			return res
		for d in os.listdir(download_rt):
			dirs=os.listdir(os.path.join(download_rt,d));
			valid_files=filter(lambda s:s.endswith('.tgz'),dirs);
			res[d]=valid_files;
		return res


HIT_STATE = (
            (1, 'New'),
            (2, 'Submitted'),
            (3, 'Graded'),
            (4, 'Finalized'),
            (5, 'Open'),
            (6, 'Active'),
            (7, 'Rejected'),
        )        
class MTHit(models.Model):
	session=models.ForeignKey(Session);

	ext_hitid=models.TextField();
	int_hitid=models.TextField();
	parameters=models.TextField();
	submitted = models.DateTimeField(auto_now_add=True);

	state=models.IntegerField(choices=HIT_STATE,default=1);

	num_required_submissions=models.IntegerField(default=0);

        def __str__(self):
          return str(self.int_hitid)

	def get_num_required_submissions(self):
            if self.num_required_submissions==0:
		return self.session.get_num_required_submissions_per_item()
	        #task_def.max_assignments
	    else:
                return self.num_required_submissions

	def get_filename(self):
		if "frame" in self.parse_parameters():
			return os.path.join(settings.DATASETS_ROOT, self.session.code, self.parse_parameters()["frame"] + ".jpg")
		elif "image_url" in self.parse_parameters():
			return self.parse_parameters()["image_url"]
		else:
			return None



	def parse_parameters(self):
		params={};
		print "P:",self.parameters
		for parm in self.parameters.split("&"):
			(k,x,v)=parm.partition("=");
			params[k.strip()]=v.strip();
		return params;

	def get_view_url(self):
		te=type.get_engine();
		return te.get_task_view_url(self)

	def get_thumbnail_url(self):
		te=type.get_engine();
		return te.get_thumbnail_url(self)

WorkUnit=MTHit
WorkItem=MTHit


MT_HIT_STATE = (
	(1, 'Active'),
	(2, 'Review'),
	(3, 'Graded'),
	(4, 'Finalized'),
	(5, 'Expired'),
        )        

class MechTurkHit(models.Model):
	session   = models.ForeignKey(Session);
	mthit     = models.ForeignKey(MTHit);
	state     = models.IntegerField(choices=MT_HIT_STATE,default=1);

	mechturk_hit_id  = models.TextField(null=True,default=None);

	tentative_grade  = models.DecimalField(max_digits=15,decimal_places=4,
					       default="0.0",
					       help_text="The tentative grade assigned to submission.");
	final_grade      = models.DecimalField(max_digits=15,decimal_places=4,
					       default="0.0",
					       help_text="The final grade assigned to submission.");


class SessionExclusion(models.Model):
	session_A = models.ForeignKey(Session,related_name='exclusionA');
	session_B = models.ForeignKey(Session,related_name='exclusionB');
	decline_reason = models.TextField(null=True,default="",blank=True);
	qualification_prefix = models.TextField(help_text="NOT IMPLEMENTED. If not empty, create unique qualification for the exclusion relation and assign qualification to workers who submit to session A. Session B will require that the qualification is not set.",blank=True,default="");

	def __str__(self):
		return "%s X %s" %(self.session_A.code,self.session_B.code);
	
	


class AssignedTask(models.Model):
	session = models.ForeignKey(Session);
	hit	= models.ForeignKey(MTHit);
	worker 	= models.TextField();

	assignment_id = models.TextField(); 
	metadata = models.TextField();

SUBMISSION_STATE = (
            (1, 'New'),
            (2, 'Graded'),
            (3, 'Approved'),
            (4, 'Rejected'),
            (5, 'Pending approval'),
            (6, 'Pending rejection'),
        )        
SUBMISSION_STATE_CAN_BE_VALID=[1,2,3,5];


SUBMISSION_APPROVAL_STATE = (
            (1, 'Not set'),
            (3, 'Approved'),
            (4, 'Rejected'),
	    )
class SubmittedTask(models.Model):
	hit = models.ForeignKey(MTHit);
	session = models.ForeignKey(Session);
	worker = models.TextField();
	assignment_id = models.TextField(); 

	response = models.TextField();

	started    = models.DateTimeField(null=True,blank=True);
	submitted  = models.DateTimeField(auto_now_add=True);

	shapes = None;
	comments = None;

	valid   = models.BooleanField(default=True);
	final_grade=models.DecimalField(max_digits=7,decimal_places=4,
                                 default="0.0",
                                 help_text="The final grade assigned to submission.");
	state   = models.IntegerField(choices=SUBMISSION_STATE,default=1);
	approval_state   = models.IntegerField(choices=SUBMISSION_APPROVAL_STATE,default=1);

	class Meta:
		permissions = (
			("can_submit_work", "Can post new submissions"),
			)
	def __str__(self):
		return str(self.id)

        def get_delay(self):
          if self.submitted and self.hit.submitted:
            return self.submitted - self.hit.submitted
          return None


	def get_comments(self): 
		v=self.get_parsed();
		return v.comments


	def get_xml_str(self):
		te=self.session.task_def.type.get_engine()
		return te.get_submission_xml(self)

	def get_timing(self):
		te=self.session.task_def.type.get_engine()
		(start,end)=te.get_work_timing(self);
		return (start,end)


	def get_parsed(self):
		#print "SELF:", self
		if self.shapes is not None:
			return self;

		te=self.session.task_def.type.get_engine()
		self.shapes = te.get_submission_xml(self)

		(GET,POST)=self.get_response();
		comment_key="Comments";
		if comment_key in GET:
			self.comments=GET[comment_key];
		elif comment_key in POST:
			self.comments=POST[comment_key];
		else:
			self.comments="";
		return self


	unpickled_response =None
	def get_response(self):
		if self.unpickled_response:
			return self.unpickled_response;
		self.unpickled_response=pickler.loads(str(self.response))
		return self.unpickled_response;


	def get_view_url(self):
		te=self.hit.session.task_def.type.get_engine();
		return te.get_submission_view_url(self)
	def get_thumbnail_url(self):
		te=self.hit.session.task_def.type.get_engine();
		return te.get_thumbnail_url(self)

	def get_grading_view_url(self,grading_params={}):
		te=self.hit.session.task_def.type.get_engine();
		try:
			return te.get_grading_view_url(self,grading_params)
		except Exception,e:
			print e
			raise

	def get_persistent_url(self):
		return settings.HOST_NAME_FOR_MTURK+"mt/submission_data_xml/"+str(self.id)+"/"+self.hit.ext_hitid+"/";
	def get_persistent_url2(self):
		return "/mt/submission_data_xml/"+str(self.id)+"/"+self.hit.ext_hitid+"/";

	def is_graded(self):
		num_active_grades=self.manualgraderecord_set.filter(valid=True).count();
		return num_active_grades>0;
WorkProduct=SubmittedTask


class Worker(models.Model):
	session = models.ForeignKey(Session,null=True, blank=True);
	worker 	= models.TextField();

	utility = models.IntegerField(default=50);
	valid   = models.BooleanField(default=True);

	def __str__(self):
		if self.session:
			return self.worker+"@"+self.session.code
		else:
			return self.worker


WORKER_PARTICIPATION_LEVEL = (
            (1, 'Newcomer'),                  #to 30  , min GPA 9.0 or 100 @ 7.0
            (2, 'Returning worker'),          #to 100 , min GPA 9.0 or 500 @ 8.0 
            (3, 'Power worker'),              #to 500 , min GPA 9.0 or to 2000, min GPA 8.0
            (4, 'Super power worker'),        #to 2000, min GPA 9.0 or to 10K @ 8.0
            (5, 'Expert'),                    #
            (6, 'Manager'),
            (7, 'Administrator'),
        )        

class WorkerProfile(models.Model):
	worker 	= models.ForeignKey(Worker);
	user    = models.ForeignKey(User,help_text="Linked user for the worker",null=True);

	level = models.IntegerField(default=1,choices=WORKER_PARTICIPATION_LEVEL);

	num_submitted = models.IntegerField(default=0);
	num_approved  = models.IntegerField(default=0);
	GPA           = models.DecimalField(max_digits=7,decimal_places=4,default="0.0");

	country       = snippets.country_field.CountryField(null=True,blank=True);
	state         = USStateField(null=True,blank=True);

	def __str__(self):
		return self.worker.worker+"["+self.get_level_display() +"]";

EXTERNAL_ENGINE = (
	(1, 'MT sandbox'),
	(2, 'MT production'),
)

WORKER_METRICS = (
	(1, 'Worker level'),
	(2, 'Num approved'),
	(3, 'Grade point average 0-100'),
)

class WorkerMetricsQualifications(models.Model):
        account       = models.ForeignKey(FundingAccount);
	engine        = models.IntegerField(default=1,choices=EXTERNAL_ENGINE);	
	metric_type   = models.IntegerField(choices=WORKER_METRICS);	
	external_id   = models.TextField(blank=True,null=True)
	def __str__(self):
		return self.account.name+"-"+self.get_metric_type_display() +"-"+self.get_engine_display()+"["+self.external_id+"]";					   



class MTurkQualification(models.Model):

	name             = models.TextField()
	qualification_def = models.ForeignKey('MTurkQualificationDefinition',null=True,blank=True);
	mt_qual_id       = models.TextField(blank=True)
	comparator       = models.TextField(help_text=" LessThan | LessThanOrEqualTo | GreaterThan | GreaterThanOrEqualTo | EqualTo | NotEqualTo | Exists  ")
	value            = models.TextField()
	qualification_url = models.URLField(blank=True);
	is_sandbox = models.BooleanField();
        def __str__(self):
          return self.name;

class MTurkQualificationDefinition(models.Model):
	name             = models.TextField()
	question         = models.TextField()
	answer           = models.TextField()
	properties       = models.TextField()
        def __str__(self):
          return self.name;

class ManualGradeRecord(models.Model):
	submission=models.ForeignKey(SubmittedTask);
	quality=models.IntegerField(default=10);
	feedback=models.TextField(blank=True);
	worker 	= models.ForeignKey(Worker,null=True, blank=True);
	valid   = models.BooleanField(default=True);
	reference = models.TextField(blank=True);

	def to_dict(self):
		return {'worker':str(self.worker),
			'valid':str(self.valid),
			'quality':str(self.quality),
			'feedback':str(self.feedback)};




class GoldStandardQualification(models.Model):
	"""We will allow N random practice assignments, M initial gold
	checking assignments and the rest of the gold standard
	assignments will be used at random with frequency R.
	
	@TODO: This will create potential problem for really high performance users
	"""
	gold_session           = models.ForeignKey(Session);

	num_gold_practice      = models.IntegerField(default=3);
	num_gold_initial       = models.IntegerField(default=3);
	random_check_frequency = models.DecimalField(max_digits=7,decimal_places=4);
	min_gold_to_block      = models.IntegerField(default=3);
	min_gpa                = models.DecimalField(max_digits=7,decimal_places=4,
                                 default="90.0",
                                 help_text="The minimum score required to pass.");
	passing_submission_grade = models.DecimalField(max_digits=7,decimal_places=4,
						       default="90.0",
						       help_text="The minimum grade for a single submission.");

	min_passing_rate         = models.DecimalField(max_digits=7,decimal_places=4,
						       default="90.0",
						       help_text="The minimum 'approval' rate.");
	def __str__(self):
		return "Min GPA %f, Gold %s" % (self.min_gpa,self.gold_session)

class WorkerTrainingProgress(models.Model):
	worker 	               = models.ForeignKey(Worker);
	gold_qual              = models.ForeignKey(GoldStandardQualification);
	num_normal_submissions = models.IntegerField(default=0);
	num_gold_submissions   = models.IntegerField(default=0);
	num_passing_submissions= models.IntegerField(default=0);
	next_check             = models.IntegerField(default=-1);
	grade_total            = models.DecimalField(max_digits=15,decimal_places=5,default="0.0")
	grade_average          = models.DecimalField(max_digits=15,decimal_places=5,default="0.0")

	def __str__(self):
		return "%s @ %s: %s g(%d),n(%d)"  % (self.worker.worker,self.gold_qual.gold_session.code,str(self.grade_average),self.num_gold_submissions,self.num_normal_submissions )

class GoldSubmission(models.Model):
	workitem    = models.ForeignKey(MTHit)
	submission  = models.ForeignKey(SubmittedTask)
	

class GoldStandardGradeRecord(models.Model):
	gold_session = models.ForeignKey(Session); #Gold session
	worker 	     = models.ForeignKey(Worker);
	workitem     = models.ForeignKey(MTHit);
	submission   = models.ForeignKey(SubmittedTask)

	performance   = models.TextField(blank=True)
	grade         = models.DecimalField(max_digits=15,decimal_places=5)
	submitted     = models.DateTimeField(auto_now_add=True);

	class Admin:
		pass

ITEM_SUBSTITUTION_STATE = (
            (1, 'Tentative'),
            (2, 'Confirmed'),
            (3, 'Cleared'),
            (4, 'Cancelled'),
)

class ItemSubstitution(models.Model):
	worker 	       = models.ForeignKey(Worker);
	requested_item = models.ForeignKey(WorkItem,related_name='substitutions_as_requested');
	shown_item     = models.ForeignKey(WorkItem,related_name='substitutions_as_shown');
	expires        = models.DateTimeField();
	state          = models.IntegerField(default=1,choices=ITEM_SUBSTITUTION_STATE);



class WorkPriorityQueueItem(models.Model):
	queue    = models.SlugField(default="");
	priority = models.IntegerField(default=40);
	work     = models.ForeignKey(WorkItem);
	assignments_left     = models.IntegerField(default=0);

	class Meta:
		ordering = ('-priority', 'id')





PAYMENT_STATE = (
            (1, 'New'),
            (2, 'Proposed'),
            (3, 'Confirmed'),
            (4, 'Cleared'),
            (5, 'AttentionNeeded'),
        )        

class Payment(models.Model):
	worker = models.ForeignKey(Worker)
	amount = models.DecimalField(max_digits=7,decimal_places=3,
                                 default="0.0",
                                 help_text="Amount to pay");
	created = models.DateTimeField(auto_now_add=True);
	state = models.IntegerField(default=1,choices=PAYMENT_STATE);
	created_by = models.ForeignKey(User,help_text="Who created the payment request",null=True);
	note = models.TextField(blank=True)
	ref  = models.TextField(blank=True)

	work_product  = models.ForeignKey(SubmittedTask)

	def __str__(self):
		return str(self.amount)+" to "+ self.worker.worker + " [" +self.get_state_display() +"]";

	class Meta:
		permissions = (
			("pay_bonus", "Can pay bonus"),
			#("confirm", "Can confirm payments"),
			)










def click_2_num(txt):
	return map(lambda v: float(v), txt.split(','));


def select_new_gold_workitem(session_id,worker):

    QUERY="""select hit.id from mturk_mthit hit 
INNER JOIN mturk_goldsubmission gold ON hit.id = gold.workitem_id
LEFT OUTER JOIN mturk_submittedtask s ON s.hit_id=hit.id and s.worker=%s where s.id is null and hit.session_id=%s limit 1
	  """
    #print QUERY
    cursor = connection.cursor()
    cursor.execute(QUERY,[worker,session_id])

    results=[];
    r=cursor.fetchone()
    if r is None:
	    return None
    hit_id=r[0];
    cursor.close();
    return WorkItem.objects.get(id=hit_id);


def worker_grading_report_complete(worker_id):

    cursor = connection.cursor()
    cursor.execute("""
SELECT mgr.quality, st.worker, st.id, h.ext_hitid
FROM `mturk_submittedtask` st, mturk_manualgraderecord mgr, mturk_mthit h
WHERE st.id = mgr.submission_id
AND h.id = st.hit_id
AND st.worker = %s
ORDER BY st.submitted DESC
""",[worker_id])
    results=[];
    try:
	for r in cursor.fetchall():
		res={'quality':r[0],
			'worker':r[1],
			'submission_id':r[2],
			'ext_hitid':r[3]};
		results.append(res);
	cursor.close();
	return results
    except:
	return None

    return None



def get_most_recent_result(session):
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute("""
 SELECT id
FROM `mturk_submittedtask`
WHERE session_id = %s
ORDER BY hit_id DESC, submitted DESC
LIMIT 1 
""",[session.id])
    try:
    	row = cursor.fetchone()
    	submission_id=row[0]
	print submission_id
	submission = SubmittedTask.objects.filter(id=submission_id)
	return submission
    except:
	return None


def get_grade_conflict_details(session,g1,g2):
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute("""
 SELECT t.id, r1.id r1_id, r1.quality q1, r2.id r1_id, r2.quality q2
FROM `mturk_submittedtask` t, mturk_manualgraderecord r1, mturk_manualgraderecord r2
WHERE t.session_id =%s
AND ( t.valid )
AND t.id = r1.submission_id
AND t.id = r2.submission_id
AND r1.valid AND r2.valid
AND r1.id <> r2.id
AND r1.quality = %s
AND r2.quality = %s
""",[session.id,g1,g2]);
    results=[];
    try:
	for r in cursor.fetchall():
		task_id=r[0];
		r1_id=r[1];
		r2_id=r[3];
		task=SubmittedTask.objects.get(id=task_id);
		r1=ManualGradeRecord.objects.get(id=r1_id);
		r2=ManualGradeRecord.objects.get(id=r2_id);
		res={'task':task,
		     'grade1':r1,
		     'grade2':r2};
		results.append(res);
	cursor.close();
	return results
    except:
	return None

    return None

def get_grade_conflict_submission_list(session,g1,g2):
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute("""
SELECT
		DISTINCT t.id id
FROM `mturk_submittedtask` t, mturk_manualgraderecord r1, mturk_manualgraderecord r2
WHERE t.session_id =%s
AND ( t.valid )
AND t.id = r1.submission_id
AND t.id = r2.submission_id
AND r1.valid AND r2.valid
AND r1.id <> r2.id
AND r1.quality = %s
AND r2.quality = %s
""",[session.id,g1,g2]);

    results=[];
    try:
	for r in cursor.fetchall():
		submission_id=r[0];
		results.append(submission_id);
	cursor.close();
	return results
    except:
	return None

    return None


def check_session_exclusions(worker,session):
    exclusions=[];

    cursor = connection.cursor()
    cursor.execute("""
select se.id,se.decline_reason from mturk_sessionexclusion se left join mturk_submittedtask st ON se.session_A_id=st.session_id  and se.session_B_id=%s and st.worker=%s where st.id is not NULL;    
""",[session.id,worker.worker]);
    try:
	for r in cursor.fetchall():
		exclusions.append((r[0],r[1]));
	cursor.close();
    except:
	pass

    return exclusions;


