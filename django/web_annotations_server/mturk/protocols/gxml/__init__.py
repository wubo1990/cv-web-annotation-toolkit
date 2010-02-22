from mturk.models import task_engines

if "gxml" not in task_engines:
    import task
    task_engines["gxml"]=task.GXmlTaskEngine();
    print task_engines

print "IMPORT GXML"
def get_task_engine():
    import task
    return task.GXmlTaskEngine();

