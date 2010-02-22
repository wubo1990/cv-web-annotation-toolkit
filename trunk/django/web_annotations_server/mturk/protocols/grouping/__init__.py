from mturk.models import task_engines

if "grouping" not in task_engines:
    import task
    task_engines["grouping"]=task.GroupingTaskEngine();
    print task_engines
