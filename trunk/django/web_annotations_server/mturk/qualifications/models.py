

from django.db import connection
from mturk.models import WorkerProfile,Worker

def compute_level(approved_count,GPA):
    if approved_count>2000 and GPA >9.0:
        return 5 #Expert
    if approved_count>10000 and GPA >8.0:
        return 5 #Expert
    if approved_count>500 and GPA >9.0:
        return 4 #Super power worker
    if approved_count>2000 and GPA >8.0:
        return 4 #Super power worker
    if approved_count>100 and GPA >9.0:
        return 3 #Power worker
    if approved_count>500 and GPA >8.0:
        return 3 #Power worker
    if approved_count>30 and GPA >9.0:
        return 2 #Returning worker
    if approved_count>100 and GPA >8.0:
        return 2 #Returning worker
    return 1 #Newcomer



def compute_worker_statistics():
    cursor = connection.cursor()

    cursor.execute("""
SELECT s.worker,sum(s.final_grade) g, sum(s.final_grade>7), count(*) c, sum(s.final_grade)/count(*) gpa  FROM `mturk_submittedtask` s where final_grade>0 group by worker order by gpa desc""")
    for row in cursor.fetchall():
        worker=row[0];
        approved_count=row[2];
        submitted_count=row[3];
        GPA=row[4];
        print worker,submitted_count,approved_count,GPA
        w,created=Worker.objects.get_or_create(worker=worker,session=None);
        if created:
            w.save()
        wp,created=WorkerProfile.objects.get_or_create(worker=w);
        wp.num_submitted=submitted_count
        wp.num_approved=approved_count
        wp.GPA=GPA
        
        wp.level=compute_level(approved_count,GPA)
        wp.save();

