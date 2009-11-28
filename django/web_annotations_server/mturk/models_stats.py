import random,math,urllib,os,sys
import cPickle as pickler

from django.contrib.auth.models import User
from django.conf import settings

from django.db import models

from django.shortcuts import render_to_response,get_object_or_404 

from django.contrib import admin

from models import *


from django.db import connection


def worker_contributions_to_session(session):
    print  "Stat worker_contributions_to_session", session, type(session.id)

    exceptional={};
    try:
	    cursor = connection.cursor()

	    cursor.execute("""
SELECT s.worker, count(*) c  FROM `mturk_submittedtask` s  left join mturk_manualgraderecord g on g.submission_id = s.id and g.valid  WHERE %s=`session_id` and g.quality>=15 group by worker
""",[session.id])

	    for r in cursor.fetchall():
		    exceptional[r[0]]=r[1];
	    cursor.close();
    except:
	    pass


    good={};
    try:
	    cursor = connection.cursor()

	    cursor.execute("""
SELECT s.worker, count(*) c  FROM `mturk_submittedtask` s  left join mturk_manualgraderecord g on g.submission_id = s.id and g.valid  WHERE %s=`session_id` and g.quality>=10 and g.quality<15 group by worker
""",[session.id])

	    for r in cursor.fetchall():
		    good[r[0]]=r[1];
	    cursor.close();
    except:
	    pass

    ok={};
    try:
	    cursor = connection.cursor()

	    cursor.execute("""
SELECT s.worker, count(*) c  FROM `mturk_submittedtask` s  left join mturk_manualgraderecord g on g.submission_id = s.id WHERE %s=`session_id` and g.quality>=7 and g.quality<10 and g.valid group by worker
""",[session.id])

	    for r in cursor.fetchall():
		    ok[r[0]]=r[1];
	    cursor.close()

    except:
	    pass


    bad={};
    try:
	    cursor = connection.cursor()

	    cursor.execute("""
SELECT s.worker, count(*) c  FROM `mturk_submittedtask` s  left join mturk_manualgraderecord g on g.submission_id = s.id WHERE %s=`session_id` and g.quality<7  and g.valid group by worker
""",[session.id])
	    for r in cursor.fetchall():
		    bad[r[0]]=r[1];
	    cursor.close()



    except:
	    pass

    
    ungraded={};
    try:
	    cursor = connection.cursor()

	    cursor.execute("""
SELECT s.worker w, count(*) FROM `mturk_submittedtask` s  left join mturk_manualgraderecord g on g.submission_id = s.id and g.valid WHERE 
%s=`session_id` and g.id is NULL group by w
""",[session.id])
	    for r in cursor.fetchall():
		    ungraded[r[0]]=r[1];
	    cursor.close()



    except:
	    pass


    total_submissions={};
    try:
	    cursor = connection.cursor()

	    cursor.execute("""
SELECT s.worker, count(*) c  FROM mturk_submittedtask s group by worker
""")
	    for r in cursor.fetchall():
		    total_submissions[r[0]]=r[1];
	    cursor.close()



    except:
	    pass

    results=[];
    try:

	    cursor = connection.cursor()

	    cursor.execute("""
SELECT worker, count( * ) c
FROM `mturk_submittedtask`
WHERE session_id = %s
GROUP BY worker
ORDER BY c DESC
""",[session.id])

	    for r in cursor.fetchall():
		w=r[0];
                #num_to_grade=r[1] - (good.get(w,0)+ ok.get(w,0) + bad.get(w,0));
                num_to_grade=ungraded.get(w,0);

		res={'worker'  :w,
		     'count'   :r[1],
		     'num_exceptional': exceptional.get(w,0),
		     'num_good': good.get(w,0),
		     'num_ok'  : ok.get(w,0),
		     'num_bad' : bad.get(w,0),
                     'total'   :total_submissions.get(w,0),
                     'num_to_grade'   :num_to_grade,
		     }
		results.append(res);

	    cursor.close();
	    return results
    except:
	return None
    return None



def submissions_counts_by_state(session):
    counts=[];

    cursor = connection.cursor()
    d=dict(SUBMISSION_STATE);

    cursor.execute("""
SELECT state, count(*) c  FROM `mturk_submittedtask` s WHERE %s=`session_id` GROUP BY state ORDER BY state
""",[session.id])

    for r in cursor.fetchall():
        counts.append({'state':r[0],'state_name':d[r[0]],'count':r[1]})
    cursor.close();


    return counts

def hit_counts_by_state(session):
    counts=[];

    cursor = connection.cursor()
    d=dict(HIT_STATE);

    cursor.execute("""
SELECT state, count(*) c  FROM `mturk_mthit` s WHERE %s=`session_id` GROUP BY state ORDER BY state
""",[session.id])

    for r in cursor.fetchall():
        counts.append({'state':r[0],'state_name':d[r[0]],'count':r[1]})
    cursor.close();

    return counts



def session_stats(session):
    from django.db import connection
    print  "Stat worker_contributions_to_session", session, type(session.id)

    grade_counts={};
    try:
	    cursor = connection.cursor()

	    cursor.execute("""
SELECT g.quality, count(*) c  FROM `mturk_submittedtask` s  left join mturk_manualgraderecord g on g.submission_id = s.id WHERE %s=`session_id` and g.valid group by g.quality
""",[session.id])

	    for r in cursor.fetchall():
                if r[0] is None:
                    grade_counts['Null']=r[1];
                else:
		    grade_counts[r[0]]=r[1];
	    cursor.close();
    except:
	    pass


    total_grades={
         'num_good': grade_counts.get(10,0)+grade_counts.get(15,0),
         'num_ok': grade_counts.get(7,0),
         'num_bad': grade_counts.get(3,0)+grade_counts.get(0,0),
         'num_ungraded': grade_counts.get('Null',0),
         }

    submissions={
        'total':session.submittedtask_set.count(),
        'approved':session.submittedtask_set.all().filter(state=3).count(),
        'rejected':session.submittedtask_set.all().filter(state=4).count(),

        'counts_by_state':submissions_counts_by_state(session)
        }
    submissions['open']=submissions['total']-(submissions['approved']+submissions['rejected']);

    timing_stats={};
    try:
	    cursor = connection.cursor()

	    cursor.execute("""
SELECT MIN(s.submitted - h.submitted), MAX(s.submitted - h.submitted), AVG(s.submitted - h.submitted), std(s.submitted - h.submitted) FROM `mturk_submittedtask` s left join mturk_mthit h on s.hit_id = h.id  where h.session_id=%s and s.session_id=%s
""",[session.id,session.id])
            r=cursor.fetchall()[0];
            timing_stats["min"]=round(r[0]);
            timing_stats["max"]=round(r[1]);
            timing_stats["avg"]=round(r[2]);
            timing_stats["std"]=round(r[3]);

	    cursor.close();
    except:
	    pass

    hit_stats={};
    hit_stats['count']=session.mthit_set.count();
    hit_stats['num_idle']=session.mthit_set.filter(state=5).count();
    hit_stats['num_active']=session.mthit_set.filter(state=6).count();

    hit_stats['counts_by_state']=hit_counts_by_state(session);

    print hit_stats
    conflicts=compute_session_conflicts(session);
    session_grades_distribution=compute_session_grade_distribution(session);

    all_stats= {'total_grades':total_grades,
                'submissions':submissions,
                'timing':timing_stats,
                'conflicts':conflicts,
                'session_grades':session_grades_distribution,
                'hits':hit_stats};

    return all_stats;

def worker_stats(worker):
    from django.db import connection

    grade_counts={};
    try:
    	    cursor = connection.cursor()

	    cursor.execute("""
SELECT g.quality, count(*) c  FROM `mturk_submittedtask` s  left join mturk_manualgraderecord g on g.submission_id = s.id WHERE  s.worker = %s and (isnull(g.valid) or g.valid) group by g.quality  
""",[worker.worker])
            print worker.worker
	    for r in cursor.fetchall():
                print r
                if r[0] is None:
                    grade_counts['Null']=r[1];
                else:
		    grade_counts[r[0]]=r[1];
	    cursor.close();
    except:
        raise
        #pass


    total_grades={
         'num_good': grade_counts.get(10,0)+grade_counts.get(15,0),
         'num_ok': grade_counts.get(7,0),
         'num_bad': grade_counts.get(3,0)+grade_counts.get(0,0),
         'num_ungraded': grade_counts.get('Null',0),
         }

    tot_submissions=0;
    if 0==0:
    #try:
	    cursor = connection.cursor()

	    cursor.execute("""
SELECT count(*) c  FROM `mturk_submittedtask` s  WHERE  s.worker = %s and s.valid
""",[worker.worker])

	    r = cursor.fetchall()[0]
            tot_submissions=r[0];
            print tot_submissions

	    cursor.close();
    #except:
# 	    pass

    num_invalid=0;
    if 0==0:
    #try:
	    cursor = connection.cursor()

	    cursor.execute("""
SELECT count(*) c  FROM `mturk_submittedtask` s  WHERE  s.worker = %s and not s.valid
""",[worker.worker])

	    r = cursor.fetchall()[0]
            num_invalid=r[0];

	    cursor.close();
    #except:
# 	    pass
            

    all_stats={'total_grades':total_grades,'num_submissions':tot_submissions,'num_invalid':num_invalid}
    return all_stats;

def format_as_table(kv,labels):
    ko=sorted(labels.keys());
    columns=[];
    for k in ko:
        columns.append(labels[k]);
    rows=[];
    for iK in ko:
        row=[];
        for jK in ko:
            if jK<iK:
                v=""
            else:
                v=kv.get((iK,jK),0);
            row.append({'v':v,'i':iK,'j':jK});
        rows.append({'label':labels[iK],'row':row});
    return {'columns':columns,'rows':rows};


def compute_session_grade_distribution(session):
    conflict_distribution={};
    def add_conflict(conflict_distribution,r):
        (id,q1,q2,c)=r;
        k=(q1,q2)
        if k not in conflict_distribution:
            conflict_distribution[k]=c;
        else:
            conflict_distribution[k]+=c;

    grades_no_conflict={};
    conflicts={};
    if 1==1:
    #try:
	    cursor = connection.cursor()

	    cursor.execute("""
 SELECT t.id, r1.quality q1, r2.quality q2, count( * )
FROM `mturk_submittedtask` t, mturk_manualgraderecord r1, mturk_manualgraderecord r2
WHERE t.session_id =%s
AND t.id = r1.submission_id
AND t.id = r2.submission_id
AND ( t.valid )
AND (0 OR ( r1.valid AND r2.valid ))
AND r1.id <> r2.id
AND r1.quality < r2.quality
GROUP BY t.id, q1, q2
""",[session.id])
            for r in cursor.fetchall():
                print "X",r
                (id,q1,q2,c)=r;
                #if id not in grades_no_conflict and id not in conflicts :
                #    grades_no_conflict[id]=r
                if id not in conflicts:
                    conflicts[id]=1;
                    #r_old=grades_no_conflict[id]
                    #del grades_no_conflict[id]
                    #add_conflict(conflict_distribution,r_old);
                    add_conflict(conflict_distribution,r);
                else:
                    conflicts[id]+=1;
                    add_conflict(conflict_distribution,r);
                
    #except:
    #    pass
    print conflict_distribution
    conflict_distribution_tbl=format_as_table(conflict_distribution,{3:'bad',7:'with_errors',10:'good',15:'exceptional'})
    #            'grades_no_conflict':grades_no_conflict,

    return {'conflict_distribution':conflict_distribution,
            'conflict_distribution_tbl':conflict_distribution_tbl,
            'conflicts':conflicts}


def compute_session_conflicts(session):
    num_conflicts=0;
    for task in session.mthit_set.all():
        has_conflicts=False
        for submission in task.submittedtask_set.filter(valid=True):
            quality_statements=[]
            for grade in submission.manualgraderecord_set.filter(valid=True):
                if grade.worker:
                    worker_utility=float(grade.worker.utility)/100;
                else:
                    worker_utility=0.5;
                quality_statements.append((grade.quality,worker_utility));
            if len(quality_statements)>0:
                tot_quality = sum([ x[1]*x[0] for x in quality_statements]);
                tot_utility = sum([ x[1] for x in quality_statements]);
                avg_quality = tot_quality / max(1,tot_utility);
                tot_disagreements= sum([ round(abs(x[0]-avg_quality)) for x in quality_statements]);
                if tot_disagreements>0:
                    has_conflicts=True
                    print task.id,quality_statements,tot_disagreements
        if has_conflicts:
            num_conflicts+=1;
    conflicts={'stats':{'num_conflicts':num_conflicts}};
    return conflicts


def workers_overview():
    from django.db import connection

    worker_grades={};
    try:
    	    cursor = connection.cursor()

	    cursor.execute("""
SELECT worker, final_grade, count( * ) c
FROM `mturk_submittedtask`
GROUP BY worker, final_grade
ORDER BY worker, final_grade
""")
	    for r in cursor.fetchall():
                (worker,grade,count)=r

                if worker not in worker_grades:
                    worker_grades[worker]={0:0,1:0,3:0,7:0,10:0,15:0};
                worker_grades[worker][grade]=count;

	    cursor.close();
            worker_utility=[]
            for w,grades in worker_grades.items():
                tot_g=sum(grades.values())
                good=grades[10]+grades[15]
                bad=grades[3]+grades[1]
                unknown=grades[0]+grades[7]
                utility=float(good)/float(max(1,(bad+good)));
                worker_utility.append((tot_g,utility,w,bad,good,unknown))
                worker_utility.sort(reverse=True)
	    cursor.close();
    except:
        raise
        #pass


    total_grades={
         'grades': worker_grades,
         'utility': worker_utility
         }
    return total_grades


def worker_to_session_contributions(worker):
    from django.db import connection

    contributions=[]
    try:
    	    cursor = connection.cursor()

	    cursor.execute("""
SELECT s.code , count( * ) c
FROM mturk_session s, `mturk_submittedtask` subm
WHERE s.id = subm.session_id
AND subm.worker = %s
GROUP BY s.id
ORDER by c DESC
""",[worker])
	    for r in cursor.fetchall():
                (session,count)=r
                contributions.append({'session':session,'count':count})
            
	    cursor.close();
    except:
        raise

    return contributions
