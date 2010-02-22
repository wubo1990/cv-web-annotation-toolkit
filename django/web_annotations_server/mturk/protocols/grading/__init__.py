from mturk.models import task_engines

if "grading" not in task_engines:
    import task
    task_engines["grading"]=task.GradingTaskEngine();

