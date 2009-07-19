import random,math,urllib,os,sys
from django.conf import settings

from mturk.protocols.task import TaskEngine


class VideoEventsTaskEngine(TaskEngine):
    def get_internal_params(self):
        return {'list_num_per_page':10,
                'frame_w':800,'frame_h':800};

    def get_base_url(self):
        return "/code/task.html?swf=video_annotation"

    def get_submission_view_url(self,submission):
        viewurl=""

        url=self.get_base_url();

        task=submission.hit;
        session=task.session;

        url=url+"&extid="+task.ext_hitid;
        
        url=url+"&session="+session.code;
        url=url+"&img_base="+urllib.quote(settings.HOST_NAME_FOR_MTURK) 
        url=url+"&task_url="+urllib.quote(settings.HOST_NAME_FOR_MTURK+"tasks/"+session.task_def.name+".xml")


        url=url+"&video_url="+task.parse_parameters()["video"];


        url=url+"&mode=display";
        url=url+"&swf_w=700&swf_h=700";
        url=url+"&instructions="+urllib.quote(session.task_def.instructions_url);
        
        annotation_url=submission.get_persistent_url()
        
        url=url+"&annotation_url="+urllib.quote(annotation_url)
        return url

    def get_thumbnail_url(self,submission):
        viewurl=""

        url=self.get_base_url();

        task=submission.hit;
        session=task.session;

        url=url+"&extid="+task.ext_hitid;
        
        url=url+"&session="+session.code;
        url=url+"&img_base="+urllib.quote(settings.HOST_NAME_FOR_MTURK) 
        url=url+"&task_url="+urllib.quote(settings.HOST_NAME_FOR_MTURK+"tasks/"+session.task_def.name+".xml")


        url=url+"&video_url="+task.parse_parameters()["video"];

        url=url+"&mode=display";
        url=url+"&display_mode=thumbnail";
        url=url+"&swf_w=300&swf_h=300";
        url=url+"&instructions="+urllib.quote(session.task_def.instructions_url);
        
        annotation_url=submission.get_persistent_url()
        
        url=url+"&annotation_url="+urllib.quote(annotation_url)
        url=url+"&comments="+urllib.quote(submission.get_comments());

        return url

    def get_grading_view_url(self,submission):
        viewurl=""

        url=self.get_base_url();

        task=submission.hit;
        session=task.session;

        url=url+"&extid="+task.ext_hitid;
        
        url=url+"&session="+session.code;
        url=url+"&img_base="+urllib.quote(settings.HOST_NAME_FOR_MTURK) 
        url=url+"&task_url="+urllib.quote(settings.HOST_NAME_FOR_MTURK+"tasks/"+session.task_def.name+".xml")


        url=url+"&video_url="+task.parse_parameters()["video"];


        url=url+"&mode=display";
        url=url+"&display_mode=thumbnail";
        url=url+"&swf_w=500&swf_h=500";
        url=url+"&instructions="+urllib.quote(session.task_def.instructions_url);
        
        annotation_url=submission.get_persistent_url()
        
        url=url+"&annotation_url="+urllib.quote(annotation_url)
        url=url+"&comments="+urllib.quote(submission.get_comments());

        return url


    def get_task_view_url(self,task_instance):
        viewurl=""

        url=self.get_base_url();

        task=self.hit;
        session=task.session;

        url=url+"&extid="+task.ext_hitid;
        
        url=url+"&session="+session.code;
        url=url+"&img_base="+urllib.quote(settings.HOST_NAME_FOR_MTURK) 
        url=url+"&task_url="+urllib.quote(settings.HOST_NAME_FOR_MTURK+"tasks/"+session.task_def.name+".xml")

        url=url+"&video_url="+task.parse_parameters()["video"];


        url=url+"&mode=input";
        url=url+"&swf_w=700&swf_h=700";
        url=url+"&instructions="+urllib.quote(session.task_def.instructions_url);
        
        return url


    def get_task_page_url(self,task,request):
        session=task.session;

        url=self.get_base_url();

        url=url+"&extid="+task.ext_hitid;

        url=url+"&session="+session.code;

        url=url+"&task="+session.task_def.name

        url=url+"&img_base="+settings.HOST_NAME_FOR_MTURK;
        
        url=url+"&mode=MT2";
        url=url+"&swf_w=700&swf_h=700";
        url=url+"&instructions="+urllib.quote(session.task_def.instructions_url);
        url=url+"&video_url="+task.parse_parameters()["video"];        
        for k,v in request.GET.items():	
            url=url+"&"+k+"="+v
        return url    



    def get_submission_xml(self,submission):
	GET,POST=submission.get_response()

	shapes_xml=urllib.unquote_plus(POST['sites']);

	return shapes_xml

    def reinterpret_task_parameters(self,task):
        return {};
        """
        xmlObj=task.parse_parameters_xml();
        sampling_node=xmlmisc.xget(xmlObj,"sampling")[0];
        overlap=float(xmlmisc.xget_a(sampling_node,"overlap"))

        layout_node=xmlmisc.xget(xmlObj,"layout")[0];
        num_per_task=int(xmlmisc.xget_a(layout_node,"num_per_task"));
        return {'overlap':overlap,'num_per_task':num_per_task};
        """
