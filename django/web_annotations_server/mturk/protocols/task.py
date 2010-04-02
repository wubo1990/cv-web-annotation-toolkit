
import sys,time

class TaskEngine:
    def get_task_view_url(self,task_instance):
        return None
    def get_submission_view_url(self,submission_instance):
        return None
    def get_thumbnail_url(self,submission_instance):
        return None

    def on_submit(self,submission):
        return None
    def on_approval(self,submission):
        return None
    def on_rejection(self,submission):
        return None
    def on_deactivate(self,submission):
        return None

    def get_edit_url(self,submission,submit_to=None):
        return None

    def get_submission_xml(self,submission):
        return ""

    def estimate_time_spent(self,submission):
        try:
            GET,POST=submission.get_response();
            st=POST['load_time'];
            et=POST['submit_time'];
            time_fmt="%a, %d %b %Y %H:%M:%S %Z"
            s= time.strptime(st,time_fmt)
            e= time.strptime(et,time_fmt)
            seconds_spent =  time.mktime(e)-time.mktime(s)
            return seconds_spent
        except Exception,e:
            print e
            return 0            

    def get_work_timing(self,submission):
        try:
            GET,POST=submission.get_response();
            st=POST['load_time'];
            et=POST['submit_time'];
            return (st,et)
        except Exception,e:
            return ('','')            

    def get_models(self):
        """ To avoid recursive dependencies, this is the only way tasks are allowed to access mturk.models
        @deprecated: It's ok now to simply do import mturk.models
        """
        import mturk.models
        return mturk.models



    def grade(self,submission,gold_session):
        raise "Not implemented" 
