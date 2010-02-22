from mturk.models import task_engines

if "attributes" not in task_engines:
    import task
    task_engines["attributes"]=task.AttributesTaskEngine();

