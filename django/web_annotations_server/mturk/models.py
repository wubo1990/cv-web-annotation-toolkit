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


#DEPRECATED: Should remove
from django.shortcuts import get_object_or_404 




class FundingAccount(models.Model):
	name=models.SlugField();
	access_key=models.CharField(max_length=25)
	secret_key=models.CharField(max_length=100);

	def __str__(self):
        	return self.name

task_engines={};
import mturk.protocols.gxml.task;
task_engines["gxml"]=mturk.protocols.gxml.task.GXmlTaskEngine();
import mturk.protocols.grading.task;
task_engines["grading"]=mturk.protocols.grading.task.GradingTaskEngine();
import mturk.protocols.video_events.task;
task_engines["video_events"]=mturk.protocols.video_events.task.VideoEventsTaskEngine();
import mturk.protocols.grouping.task;
task_engines["grouping"]=mturk.protocols.grouping.task.GroupingTaskEngine();

import mturk.protocols.attributes.task;
task_engines["attributes"]=mturk.protocols.attributes.task.AttributesTaskEngine();

class TaskType(models.Model):
	name=models.SlugField();
	
	def get_engine(self):
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



SESSION_STATE = (
            (1, 'Active'),
            (2, 'HasAllTasks'),
            (3, 'HasAllSubmissions'),
            (4, 'HasAllGrades'),
            (5, 'Finalized'),
        )        
class Session(models.Model):
	code=models.SlugField();
	task_def=models.ForeignKey(Task);
	funding=models.ForeignKey(FundingAccount);

	standalone_mode = models.BooleanField(default=False);
	sandbox         = models.BooleanField(default=True);
	HITlimit        = models.IntegerField(default=100);

	parameters=models.TextField(null=True, blank=True); #depreciated

        owner=models.ForeignKey(User, null=True, blank=True)

	hit_type=models.CharField(max_length=100,
                                  blank=True,
				  default="",
                                  help_text="mechanical turk's id");

	state=models.IntegerField(choices=SESSION_STATE,default=1);

	
	gold_standard_qualification = models.ForeignKey('GoldStandardQualification',null=True,blank=True);
	mturk_qualification = models.ManyToManyField('MTurkQualification',blank=True,null=True);

	def parse_parameters(self):
		return {};
	
	def __str__(self):
        	return self.code

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

	#mt_hitid=models.TextField(null=True,defalut=null);
	ext_hitid=models.TextField();
	int_hitid=models.TextField();
	parameters=models.TextField();
	submitted = models.DateTimeField(auto_now_add=True);

	state=models.IntegerField(choices=HIT_STATE,default=1);


        def __str__(self):
          return str(self.int_hitid)

	def get_filename(self):
          return os.path.join(settings.DATASETS_ROOT, self.session.code, self.parse_parameters()["frame"] + ".jpg")

	def parse_parameters(self):
		params={};
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
        )        
class SubmittedTask(models.Model):
	hit = models.ForeignKey(MTHit);
	session = models.ForeignKey(Session);
	worker = models.TextField();
	assignment_id = models.TextField(); 

	response = models.TextField();

	started    = models.DateTimeField(null=True,blank=True);
	submitted = models.DateTimeField(auto_now_add=True);

	shapes = None;
	comments = None;

	valid   = models.BooleanField(default=True);
	final_grade=models.DecimalField(max_digits=7,decimal_places=4,
                                 default="0.0",
                                 help_text="The final grade assigned to submission.");
	state   = models.IntegerField(choices=SUBMISSION_STATE,default=1);

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
		print self
		return te.get_submission_xml(self)

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

	"""

		if not self.session.parameters:
			protocol="g-xml"
		else:
			sParm=self.session.parse_parameters();
			protocol=sParm['protocol'];

		if protocol=="people14":
			(shapes,comments)=people14_parse_submission(self)

			#print self
		elif protocol=="g-outlets" or protocol=="g-xml":
			(shapes_xml,comments)=g_xml_parse_submission(self)
			self.shapes=shapes_xml;
			self.comments=comments;
			#print self
		else:
			raise "Error: unknown protocol "+protocol
		return self;
		"""
	def get_view_url(self):
		te=self.hit.session.task_def.type.get_engine();
		return te.get_submission_view_url(self)
	def get_thumbnail_url(self):
		te=self.hit.session.task_def.type.get_engine();
		return te.get_thumbnail_url(self)
	def get_grading_view_url(self):
		te=self.hit.session.task_def.type.get_engine();
		print "GV"
		return te.get_grading_view_url(self)

	def get_persistent_url(self):
		return settings.HOST_NAME_FOR_MTURK+"mt/submission_data_xml/"+str(self.id)+"/"+self.hit.ext_hitid+"/";
	def get_persistent_url2(self):
		return "/mt/submission_data_xml/"+str(self.id)+"/"+self.hit.ext_hitid+"/";

	def is_graded(self):
		print "IS_GRADED?"
		num_active_grades=self.manualgraderecord_set.filter(valid=True).count();
		print num_active_grades
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



class GoldStandardQualification(models.Model):
	gold_session = models.ForeignKey(Session);

	num_tasks              = models.IntegerField(default=3);
	random_check_frequency = models.DecimalField(max_digits=7,decimal_places=4);
	min_score              = models.DecimalField(max_digits=7,decimal_places=4,
                                 default="100.0",
                                 help_text="The minimum score required to pass.");


class MTurkQualification(models.Model):

	name             = models.TextField()
	qualification_def = models.ForeignKey('MTurkQualificationDefinition',null=True,blank=True);
	mt_qual_id       = models.TextField(blank=True)
	comparator       = models.TextField()
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

class GoldStandardGradeRecord(models.Model):
	session = models.ForeignKey(Session);
	worker 	= models.ForeignKey(Worker);
	hit 	= models.ForeignKey(MTHit);

	performance = models.TextField()
	grade 	= models.TextField()
	submitted = models.DateTimeField(auto_now_add=True);

	class Admin:
		pass



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






def select_sample_task(session):
	try:
		sample=session.mthit_set.all()[0]
		print sample
	except IndexError:
		return None;

	return sample	




def random_task_i_havent_done(session,workerId):
    from django.db import connection
    cursor = connection.cursor()
    print  session, type(session.id), workerId
    cursor.execute("""
 SELECT count( hid )
FROM (

SELECT hits.id hid, st.worker w
FROM mturk_mthit hits
LEFT OUTER JOIN mturk_submittedtask st ON hits.id = st.hit_id
AND st.worker = %s
WHERE hits.session_id =%s

) tmp
WHERE w IS NULL 
""",[workerId,session.id])
    try:
    	row = cursor.fetchone()
    	numAvailableTasks=row[0]
	print numAvailableTasks
	if  numAvailableTasks==0:
		return None
    except:
	return None
    print 'row',row
    print 'numAvailableTasks',numAvailableTasks
    	
    selectedTask=random.randint(1,numAvailableTasks);
    print 'selectedTask',selectedTask
    cursor.execute("""
 SELECT  hid 
FROM (

SELECT hits.id hid, st.worker w
FROM mturk_mthit hits
LEFT OUTER JOIN mturk_submittedtask st ON hits.id = st.hit_id
AND st.worker = %s
WHERE hits.session_id =%s
) tmp
WHERE w IS NULL LIMIT 1 OFFSET %s
""",[workerId,session.id,selectedTask-1])	#Stupid SQL. It sided with python in 0-based counting.

    try:
    	row = cursor.fetchone()
    	taskID=row[0]
	print taskID
    	cursor.close();
    except:
	return None

    return taskID


def task_w_least_coverage(session,workerId):
    from django.db import connection
    cursor = connection.cursor()
    print workerId, session.id
    cursor.execute("""
 SELECT hid, count( stCounts.id ) totalCount
FROM (

SELECT hits.id hid, st.worker w
FROM mturk_mthit hits
LEFT OUTER JOIN mturk_submittedtask st ON hits.id = st.hit_id
AND st.worker = %s
WHERE hits.session_id = %s
)tmp LEFT OUTER JOIN  mturk_submittedtask stCounts
ON stCounts.hit_id = tmp.hid
WHERE w IS NULL
GROUP BY hid
ORDER BY totalCount
LIMIT 1
""",[workerId,session.id])
    try:
	all_rows = cursor.fetchall();
	print all_rows
	if len(all_rows)==0:
		taskID=None
	else:
	    	selectedTask=random.randint(0,len(all_rows)-1);	
    		taskID=all_rows[selectedTask][0];
	print "Selected task:",taskID
    	cursor.close();
    except:
	return None

    return taskID



def random_task_nobody_have_done(session):
    from django.db import connection
    cursor = connection.cursor()
    #DOES NOT WORK NOW
    cursor.execute("""
 SELECT count( hid )
FROM (

SELECT hits.id hid, st.worker w
FROM mturk_mthit hits
LEFT OUTER JOIN mturk_submittedtask st ON hits.id = st.hit_id
AND st.worker = %s
WHERE hits.session_id =%s

) tmp
WHERE w IS NULL 
""",[workerId,session.id])
    try:
    	row = cursor.fetchone()
    	numAvailableTasks=row[0]
	print numAvailableTasks
	if  numAvailableTasks==0:
		return None
    except:
	return None
    print 'row',row
    print 'numAvailableTasks',numAvailableTasks
    	
    selectedTask=random.randint(1,numAvailableTasks);
    print 'selectedTask',selectedTask
    cursor.execute("""
 SELECT  hid 
FROM (

SELECT hits.id hid, st.worker w
FROM mturk_mthit hits
LEFT OUTER JOIN mturk_submittedtask st ON hits.id = st.hit_id
AND st.worker = %s
WHERE hits.session_id =%s
) tmp
WHERE w IS NULL LIMIT 1 OFFSET %s
""",[workerId,session.id,selectedTask-1])	#Stupid SQL. It sided with python in 0-based counting.

    try:
    	row = cursor.fetchone()
    	taskID=row[0]
	print taskID
    	cursor.close();
    except:
	return None

    return taskID



def random_task_i_havent_done_w_powerlaw(session,workerId):
    from django.db import connection
    cursor = connection.cursor()
    print  session, type(session.id), workerId
    cursor.execute("""
SELECT hits.id hid,count(st2.id)+1 as total FROM mturk_mthit hits LEFT OUTER JOIN mturk_submittedtask st 
ON hits.id=st.hit_id and %s=st.worker LEFT OUTER JOIN mturk_submittedtask st2 
 ON hits.id=st2.hit_id
WHERE hits.session_id = %s AND ( st.worker <> %s or st.worker is NULL) 
GROUP BY hid
""",[workerId,session.id,workerId])

    try:
	total=0;
	counts=[];
	for row in cursor.fetchall():
		numResults=row[1];
		total=total+numResults;
		counts.append((row[0],row[1],total));
	
    	cursor.close()
    except:
	return None

    if total==0:
	return None;
    print total
    selectedCount=random.randint(1,total);
    selectedTask=None
    for iC,c in enumerate(counts):
	if c[2]<=selectedCount:
		selectedTask=c[0];
		break

    return selectedTask


def random_task_from_gold_standard(session,GSsession,workerId):
    from django.db import connection
    cursor = connection.cursor()
    print  session.id, GSsession.id, workerId

	#Why do I need st2 here??
    cursor.execute("""
SELECT hits.id hid
FROM mturk_mthit hits
JOIN mturk_mthit GS_hits ON hits.int_hitid = GS_hits.int_hitid
AND %s = GS_hits.session_id
LEFT OUTER JOIN mturk_submittedtask st ON hits.id = st.hit_id
AND %s = st.worker
LEFT OUTER JOIN mturk_submittedtask st2 ON hits.id = st2.hit_id
WHERE hits.session_id = %s
AND (
st.worker <> %s
OR st.worker IS NULL
)
GROUP BY hid
""",[GSsession.id,workerId,session.id,workerId])

    try:
	counts=[];
	for row in cursor.fetchall():
		counts.append(row[0]);
    	if len(counts)==0:
		return None;
    	selectedTaskIdx=random.randint(0,len(counts)-1);	
	selectedTask=counts[selectedTaskIdx];
	
    	cursor.close()
    except:
	return None

    return selectedTask


def select_next_task(session,workerId):
	try:
		sParm=session.parse_parameters();
		bTaskSelected=False;
		bFromGoldStandard=False;
		if not bTaskSelected and 'P_gs' in sParm and 'GS_session' in sParm:
			pGoldStandard=int(sParm['P_gs']);
			decision=random.randint(1,100);
			print "DDD",decision,pGoldStandard
			if decision<=pGoldStandard:
				GoldStandard_session_code=sParm['GS_session'];
				print GoldStandard_session_code
				GoldStandard_session = get_object_or_404(Session,code=GoldStandard_session_code)

				task=random_task_from_gold_standard(session,GoldStandard_session,workerId);
				print task
				if task is not None:
					bFromGoldStandard=True;
					bTaskSelected=True;

		if not bTaskSelected and 'P_powerlaw' in sParm:
			pPowerLaw=int(sParm['P_powerlaw']);
			decision=random.randint(1,100);
			if decision<=pPowerLaw:
				print "Pick task for powerlaw distribution"
				task=random_task_i_havent_done_w_powerlaw(session,workerId);
				bTaskSelected=True;



		if not bTaskSelected and 'P_uniformly_at_random' in sParm:
			print "Pick task uniformly at random"
			pUniform=int(sParm['P_uniformly_at_random']);
			pUniform=random.randint(1,100);
			task=random_task_i_havent_done(session,workerId);
			bTaskSelected=True;

		if not bTaskSelected:
			print "Pick task with least coverage."
			task=task_w_least_coverage(session,workerId);
			bTaskSelected=True;

		if task is None:
			return (None,False)
		sample=MTHit.objects.get(id=task);
		print sample
		print sample.session.id
	except IndexError:
		raise
		return (None,False)	


	return (sample,bFromGoldStandard)
		





def score_worker(worker,gold_standard_hit,GoldStandard_session,task,session,submission):
	sParm=session.parse_parameters();
	protocol=sParm['protocol'];
	if protocol=="people14":
		groundtruth_shapes=[];
		for GS_submission in gold_standard_hit.submittedtask_set.all():
			groundtruth_shapes=GS_submission.get_parsed().shapes;
			break
			#GET,POST=pickler.loads(GS_submission.response)
			#parse1=POST['sites'].split(";")
			#locations=parse1[3:17]
			#locations_xy=map(lambda s:map(lambda v:float(v),s.split(",")[0:2]),locations);
			#all_locations.append(locations_xy);
		#print all_locations
		#average_locations=all_locations[0];
		#for l in all_locations[1:]:
		#	average_locations=map(lambda a,b:a+b,average_locations,l);
		#N=len(all_locations);
		#print average_locations
		#average_locations=map(lambda v:map(lambda x:x/N,v),average_locations);
		#print average_locations

		worker_submission=submission.get_parsed().shapes;
		
		if len(worker_submission)==0 and len(groundtruth_shapes)==0:
			performance='no data'
			delta_utility=1;					
		elif len(worker_submission)==0 and len(groundtruth_shapes)>0:
			performance='missing_shapes';
			delta_utility=-10;
		elif len(worker_submission)>0 and len(groundtruth_shapes)==0:
			performance='spurious_shapes';
			delta_utility=-1;
		else:
			#GET,POST=pickler.loads(str(submission.response))
			#parse1=POST['sites'].split(";")
			#locations=parse1[3:17]
			#locations_xy=map(lambda s:map(lambda v:float(v),s.split(",")[0:2]),locations);

			def compute_error(a,b,k):
				if k==1:
					return 0;

				error=0;
				print "CE:", 		
				for v1,v2 in map(None,a,b):
					diff2=map(lambda x,y:(x-y)*(x-y),a,b);
					error+=math.sqrt(sum(diff2));		
					print math.sqrt(sum(diff2)),
				print 		
				return error
			#difference=map(compute_error,average_locations,locations_xy);
			#average_distance=sum(difference)/len(average_locations);
			correspondence={};
			for s in worker_submission:
				bestV=1000000;
				bestI=-1;
				cS=s['center'];
				for iGt,gt in enumerate(groundtruth_shapes):
					cG=gt['center'];
					dX=cS[0]-cG[0];
					dY=cS[1]-cG[1];
					d=dX*dX+dY*dY;
					if d<bestV:
						bestV=d;
						bestI=iGt
				correspondence[s['label']]=(bestI,bestV)
			print "--------------------------"
			print 
			print correspondence
			print groundtruth_shapes
			print worker_submission
			print "==============="
			quality=0;
			for s in worker_submission:
				bestI=correspondence[s['label']][0];
				P1=map(lambda v:(v[0],v[1]),s['points']);
				K1=map(lambda v:v[3],s['points']);
				P2=map(lambda v:(v[0],v[1]),groundtruth_shapes[bestI]['points']);
				#compute point-wise difference
				difference=map(compute_error,P1,P2,K1);
				#print difference
				average_distance=sum(difference)/len(difference);
				quality=quality+average_distance;

			quality=quality/len(worker_submission);
			print quality
	
			reward_map=[ 	(-1,  5,  +10), 
					( 5, 10,  +5), 
					(10, 15,  +1), 
					(15, 20,   0), 
					(20, 40, -10), 
					(40, 1000000, -20) ];
			delta_utility=-100;
			for iR,r in enumerate(reward_map):
				if average_distance>r[0] and average_distance<=r[1]:
					delta_utility=r[2];
			performance=str(average_distance)

		grading_report=GoldStandardGradeRecord(session=session,worker=worker,hit=task,
					performance=performance,grade=delta_utility);

		worker.utility = min(100,worker.utility+delta_utility);
		grading_report.save();
		worker.save();
		return grading_report
	else:
		print "Unsupported protocol"
		return None



def people14_parse_submission(submission):
	GET,POST=pickler.loads(str(submission.response))

	shapes=POST['sites'].split(";;")
	comments=POST['Comments'];

	all_shapes=[];
	for s in shapes[1:]:
		tokens=s.split(";");
		shape_label=tokens[0];
		level1=tokens[2:4];
		level2=tokens[5:];
		#print level1
		#print level2;
		if len(level2)==0:
			continue
				
		pt1=click_2_num(level1[0])[0:2];
		pt2=click_2_num(level1[1])[0:2];
		(w,h)=map(lambda x,y:x-y,pt2,pt1);
		s=max(w,h);

		scale=s/500.0;
		wN=w/scale;
		hN=h/scale;
		oX2=(500-wN)/2;
		oY2=(500-hN)/2;
		oX1=pt1[0];
		oY1=pt1[1];


		def point2frame(str_pt):
			pt=str_pt.split(',');
			x=float(pt[0]);
			y=float(pt[1]);
			newX=(x-oX2)*scale+oX1;
			newY=(y-oY2)*scale+oY1;
			return (newX,newY,float(pt[2]),float(pt[3]));

		l2points=map(point2frame,level2);

		torso=l2points[2:4]+l2points[8:10];
		if len(torso)==0:
			continue
		mX=0;mY=0;
		for pt in torso:
			(x,y)=pt[0:2];
			mX=mX+x;
			mY=mY+y;
		mX=mX/len(torso);
		mY=mY/len(torso);
		#print mX,mY

		shape={'label':shape_label,
			'center':(mX,mY),
			'points':l2points,
			'torso':torso,
			'box':[pt1,pt2]};
		all_shapes.append(shape);

	return (all_shapes,comments);



def people14_get_gs_annotation(session,gs_session,gold_standard_hit):
	sParm=session.parse_parameters();
	protocol=sParm['protocol'];
	if protocol=="people14":
		all_locations=[];
		for GS_submission in gold_standard_hit.submittedtask_set.filter(session=gs_session):
			groundtruth_shapes=GS_submission.get_parsed().shapes;
			return groundtruth_shapes
			#GET,POST=pickler.loads(GS_submission.response)
			#parse1=POST['sites'].split(";")
			#locations=parse1[3:17]
			#locations_xy=map(lambda s:map(lambda v:float(v),s.split(",")[0:2]),locations);
			#all_locations.append(locations_xy);
		#print all_locations
		#average_locations=all_locations[0];
		#for l in all_locations[1:]:
		#	average_locations=map(lambda a,b:a+b,average_locations,l);
		#N=len(all_locations);
		#print average_locations
		#average_locations=map(lambda v:map(lambda x:x/N,v),average_locations);
		#return average_locations
		return None
	else:
		return None


def click_2_num(txt):
	return map(lambda v: float(v), txt.split(','));

def get_existing_locations(session,hit):
	sParm=session.parse_parameters();
	protocol=sParm['protocol'];
	if protocol=="people14":
		all_locations=[];
		target=(500,500);
		existing_locations=[];
		
		if not 'GS_session' in sParm:
			return [];

		GoldStandard_session_code=sParm['GS_session'];
		gs_session = get_object_or_404(Session,code=GoldStandard_session_code)
		gold_standard_hit=gs_session.mthit_set.filter(int_hitid=hit.int_hitid)[0];

		for GS_submission in gold_standard_hit.submittedtask_set.all():
			GET,POST=pickler.loads(GS_submission.response)
			print POST
			shapes=POST['sites'].split(";;")
			print shapes
			for s in shapes[1:]:
				tokens=s.split(";");
				level1=tokens[2:4];
				level2=tokens[5:];
				print level1
				print level2;
				if len(level1)==0:
					continue
				
				pt1=click_2_num(level1[0])[0:2];
				pt2=click_2_num(level1[1])[0:2];
				(w,h)=map(lambda x,y:x-y,pt2,pt1);
				s=max(w,h);

				torso=level2[2:4]+level2[8:10];
				mX=0;mY=0;
				for pt in torso:
					(x,y)=click_2_num(pt)[0:2];
					mX=mX+x;
					mY=mY+y;
				mX=mX/len(torso);
				mY=mY/len(torso);
				print mX,mY

				scale=s/500.0;
				wN=w/scale;
				hN=h/scale;
				oX=(500-wN)/2;
				oY=(500-hN)/2;
				mX=(mX-oX)*scale+pt1[0];
				mY=(mY-oY)*scale+pt1[1];
				existing_locations.append((mX,mY));
			break;
		return existing_locations
	else:
		return None




def stats_worker_contributions_perfect():
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute("""
SELECT worker, count( sid ) num_sessions, sum( contribution ) total_contribution
FROM (

SELECT st.worker worker, st.session_id sid, count( st.hit_id ) contribution
FROM `mturk_submittedtask` st, mturk_manualgraderecord mgr
WHERE mgr.submission_id = st.id
AND mgr.quality >9
GROUP BY worker, st.session_id
)tmp
GROUP BY worker
ORDER BY total_contribution DESC 
""")
    results=[];
    try:
	for r in cursor.fetchall():
		res={'worker':r[0],
			'num_sessions':r[1],
			'contribution':r[2]};
		results.append(res);
	cursor.close();
	return results
    except:
	return None

    return None



def stats_worker_contributions_any():
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute("""
SELECT worker, count( sid ) num_sessions, sum( contribution ) total_contribution
FROM (

SELECT st.worker worker, st.session_id sid, count( st.hit_id ) contribution
FROM `mturk_submittedtask` st
GROUP BY worker, st.session_id
)tmp
GROUP BY worker
ORDER BY total_contribution DESC 
""")
    results=[];
    try:
	for r in cursor.fetchall():
		res={'worker':r[0],
		     'num_sessions':r[1],
		     'contribution':r[2]};
		results.append(res);
	cursor.close();
	return results
    except:
	return None

    return None





def stats_submissions_per_session():
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute("""
SELECT s.code, session_id, count( * )
FROM `mturk_submittedtask`
LEFT JOIN mturk_session s ON s.id = session_id
GROUP BY session_id
ORDER BY session_id DESC
""")
    results=[];
    try:
	for r in cursor.fetchall():
		res={'session_code':r[0],
			'session_id':r[1],
			'submissions':r[2]};
		results.append(res);
	cursor.close();
	return results
    except:
	return None

    return None



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
 SELECT		DISTINCT t.id id
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

def get_grading_tasks_for_grading_submission(session,grading_session,worker_code,task_id):
	results=[];
	return results




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

    ''' #Removing the check on the inverted exclusion. This makes the exclusions directed!
    cursor = connection.cursor()
    cursor.execute("""
select se.id,se.decline_reason from mturk_sessionexclusion se left join mturk_submittedtask st ON se.session_A_id=%s  and se.session_B_id=st.session_id and st.worker=%s where st.id is not NULL;    
""",[session.id,worker.worker]);
    try:
	for r in cursor.fetchall():
		exclusions.append((r[0],r[1]));
	cursor.close();
    except:
	pass
	'''
    return exclusions;

