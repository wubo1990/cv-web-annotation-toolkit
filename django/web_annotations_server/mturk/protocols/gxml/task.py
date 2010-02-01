import random,math,urllib,os,sys
from django.conf import settings

from mturk.protocols.task import TaskEngine

from datastore import xmlmisc

import xml.dom.minidom
from xml.dom.minidom import Node


class GXmlTaskEngine(TaskEngine):
    def get_internal_params(self):
        return {'list_num_per_page':10,
                'frame_w':800,'frame_h':800};

    def get_submission_view_url(self,submission):
        viewurl=""

        url="/code/task.html?swf=label_generic"

        task=submission.hit;
        session=task.session;

        url=url+"&extid="+task.ext_hitid;
        
        url=url+"&session="+session.code;
        url=url+"&img_base="+urllib.quote(settings.HOST_NAME_FOR_MTURK) 
        url=url+"&task_url="+urllib.quote(settings.HOST_NAME_FOR_MTURK+"tasks/"+session.task_def.name+".xml")

        url=url+self.get_frame_part(session,task);



        url=url+"&mode=display";
        url=url+"&swf_w=700&swf_h=700";
        url=url+"&instructions="+urllib.quote(session.task_def.instructions_url);
        
        annotation_url=submission.get_persistent_url()
        
        url=url+"&annotation_url="+urllib.quote(annotation_url)
        return url

    def get_thumbnail_url(self,submission):
        viewurl=""

        url="/code/task.html?swf=label_generic"

        task=submission.hit;
        session=task.session;

        url=url+"&extid="+task.ext_hitid;
        
        url=url+"&session="+session.code;
        url=url+"&img_base="+urllib.quote(settings.HOST_NAME_FOR_MTURK) 
        url=url+"&task_url="+urllib.quote(settings.HOST_NAME_FOR_MTURK+"tasks/"+session.task_def.name+".xml")

        url=url+self.get_frame_part(session,task);



        url=url+"&mode=display";
        url=url+"&display_mode=thumbnail";
        url=url+"&swf_w=300&swf_h=300";
        url=url+"&instructions="+urllib.quote(session.task_def.instructions_url);
        
        annotation_url=submission.get_persistent_url()
        
        url=url+"&annotation_url="+urllib.quote(annotation_url)
        url=url+"&comments="+urllib.quote(submission.get_comments());

        return url

    def get_grading_view_url(self,submission,grading_parameters={}):
        viewurl=""

        url="/code/task.html?swf=label_generic"

        task=submission.hit;
        session=task.session;

        url=url+"&extid="+task.ext_hitid;
        
        url=url+"&session="+session.code;
        url=url+"&img_base="+urllib.quote(settings.HOST_NAME_FOR_MTURK) 
        url=url+"&task_url="+urllib.quote(settings.HOST_NAME_FOR_MTURK+"tasks/"+session.task_def.name+".xml")


        url=url+self.get_frame_part(session,task);

        url=url+"&mode=display";
        url=url+"&display_mode="+grading_parameters.get("display_mode","thumbnail");
        url=url+"&swf_w=700&swf_h=700";
        url=url+"&instructions="+urllib.quote(session.task_def.instructions_url);
        
        annotation_url=submission.get_persistent_url()
        
        url=url+"&annotation_url="+urllib.quote(annotation_url)
        url=url+"&comments="+urllib.quote(submission.get_comments());

        return url


    def get_task_view_url(self,task_instance):
        viewurl=""

        url="/code/task.html?swf=label_generic"

        task=self.hit;
        session=task.session;

        url=url+"&extid="+task.ext_hitid;
        
        url=url+"&session="+session.code;
        url=url+"&img_base="+urllib.quote(settings.HOST_NAME_FOR_MTURK) 
        url=url+"&task_url="+urllib.quote(settings.HOST_NAME_FOR_MTURK+"tasks/"+session.task_def.name+".xml")


        url=url+self.get_frame_part(session,task);



        url=url+"&mode="+task.parse_parameters().get("mode","input");
        if "annotation_url" in task.parse_parameters():
            url=url+"&annotation_url="+urllib.quote(task.parse_parameters()["annotation_url"])
        url=url+"&swf_w=700&swf_h=700";
        url=url+"&instructions="+urllib.quote(session.task_def.instructions_url);
        
        return url


    def get_task_page_url(self,task,request):
        session=task.session;

        url="/code/task.html?swf=label_generic"

        url=url+"&extid="+task.ext_hitid;

        url=url+"&session="+session.code;

        url=url+"&task="+session.task_def.name

        url=url+"&video="+session.code;

        url=url+self.get_frame_part(session,task);
        url=url+"&img_base="+settings.HOST_NAME_FOR_MTURK;
        
        url=url+"&mode="+task.parse_parameters().get("mode","MT2");
        if "annotation_url" in task.parse_parameters():
            url=url+"&annotation_url="+urllib.quote(task.parse_parameters()["annotation_url"])
        url=url+"&swf_w=700&swf_h=700";
        url=url+"&instructions="+urllib.quote(session.task_def.instructions_url);
        
        for k,v in request.GET.items():	
            url=url+"&"+k+"="+v
        return url    

    def get_frame_part(self,session,task):
        params=task.parse_parameters();
        if "frame" in params:
            #url=url+"&frame="+()["frame"];
            return "&image_url="+urllib.quote(settings.HOST_NAME_FOR_MTURK+"frames/"+session.code+ \
                                                  "/"+params["frame"]+".jpg");
        else:
            return "&image_url="+params["image_url"]

    def get_submission_xml(self,submission):
	GET,POST=submission.get_response()

	shapes_xml=urllib.unquote_plus(POST['sites']);
        #return shapes_xml
        try:
            x_doc = xml.dom.minidom.parseString(shapes_xml)
        except:
            x_doc=xml.dom.minidom.Document();
            x_res = x_doc.createElement("results")
            x_doc.appendChild(x_res);

        x_ref = x_doc.createElement("submission")
        x_doc.documentElement.appendChild(x_ref);

        #reference data
        x_ref.setAttribute("ref-session",str(submission.session.code));
        x_ref.setAttribute("ref-hit",submission.hit.ext_hitid);
        x_ref.setAttribute("ref-submission",str(submission.id));
        x_ref.setAttribute("id",str(submission.id));
        x_ref.setAttribute("worker",str(submission.worker));
        x_ref.setAttribute("url",submission.get_persistent_url());

	return x_doc.toxml()


    def estimate_time_spent(self,submission):
        GET,POST=submission.get_response();
        try:
            st=POST['load_time'];
            et=POST['submit_time'];
            time_fmt="%a, %d %b %Y %H:%M:%S %Z"
            s= time.strptime(st,time_fmt)
            e= time.strptime(et,time_fmt)
            seconds_spent =  time.mktime(e)-time.mktime(s)
            return seconds_spent
        except Exception,e:
            shapes_xml=urllib.unquote_plus(POST['sites']);
            try:
                x_doc = xml.dom.minidom.parseString(shapes_xml)
                meta_node=xmlmisc.xget(x_doc,"meta")[0];
                load_time=float(xmlmisc.xget_a_d(meta_node,"load_time","0"));
                submit_time=float(xmlmisc.xget_a_d(meta_node,"submit_time","0"));
                return (submit_time-load_time)/1000;
            except:
                return 0

