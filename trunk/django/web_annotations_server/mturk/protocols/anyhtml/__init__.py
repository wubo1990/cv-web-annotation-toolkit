from mturk.models import task_engines

if "anyhtml" not in task_engines:
    import task
    task_engines["anyhtml"]=task.AnyHTMLTaskEngine();

