from mturk.models import task_engines

if "video_events" not in task_engines:
    import task
    task_engines["video_events"]=task.VideoEventsTaskEngine();

