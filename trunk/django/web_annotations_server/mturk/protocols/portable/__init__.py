from mturk.models import task_engines

if "portable" not in task_engines:
    import task
    task_engines["portable"]=task.PortableTaskEngine();

print "IMPORT PORTABLE"
def get_task_engine():
    import task
    return task.GXmlTaskEngine();

