import random,math,urllib,os,sys
from django.conf import settings
from django.shortcuts import get_object_or_404 

from datastore import xmlmisc
from xml.dom import minidom
from mturk.protocols.task import TaskEngine
import cPickle as pickler

class GroupingTaskEngine(TaskEngine):
    def get_internal_params(self):
        return {'list_num_per_page':10,
                'frame_w':800,'frame_h':600};

    def get_base_url(self):
        return "/code/grouping.html?"


    def get_thumbnail_url(self,submission):
        return self.get_submission_view_url(submission)

    def get_submission_view_url(self,submission):
        hit=submission.hit;
        session=hit.session;

        url=self.get_base_url()

        url=url+"mode=display";
        url=url+"&extid="+hit.ext_hitid;

        url=url+"&session="+session.code;

        url=url+"&task="+session.task_def.name

        url=url+"&video="+session.code;
        url=url+"&img_base="+settings.HOST_NAME_FOR_MTURK;
        url=url+"&instructions="+urllib.quote(session.task_def.instructions_url);

        hit_parameters_url=settings.HOST_NAME_FOR_MTURK+"mt/hit_parameters/"+hit.ext_hitid+"/";
        url=url+"&data_url="+urllib.quote(hit_parameters_url);

        url=url+"&annotation_url="+urllib.quote(submission.get_persistent_url2());
        url=url+"&parameters_url="+urllib.quote(settings.HOST_NAME_FOR_MTURK+"tasks/"+session.task_def.name+".xml")

        return url


    def get_grading_view_url(self,submission):
        return self.get_submission_view_url(submission)


    def reinterpret_task_parameters(self,task):
        xmlObj=task.parse_parameters_xml();
        #@sampling_node=xmlmisc.xget(xmlObj,"sampling")[0];
        #overlap=float(xmlmisc.xget_a(sampling_node,"overlap"))

        #layout_node=xmlmisc.xget(xmlObj,"layout")[0];
        #num_per_task=int(xmlmisc.xget_a(layout_node,"num_per_task"));
        return {} #{'overlap':overlap,'num_per_task':num_per_task};

    def get_models(self):
        print sys.modules.keys()
        return sys.modules["web_annotations_server.mturk.models"]


    def get_task_page_url(self,task,request):
        session=task.session;

        url=self.get_base_url()

        url=url+"&extid="+task.ext_hitid;

        url=url+"&session="+session.code;

        url=url+"&task="+session.task_def.name

        url=url+"&video="+session.code;
        url=url+"&img_base="+settings.HOST_NAME_FOR_MTURK;
        url=url+"&mode=input";
        url=url+"&instructions="+urllib.quote(session.task_def.instructions_url);
        hit_parameters_url=settings.HOST_NAME_FOR_MTURK+"mt/hit_parameters/"+task.ext_hitid+"/";
        url=url+"&data_url="+urllib.quote(hit_parameters_url);
        url=url+"&parameters_url="+urllib.quote(settings.HOST_NAME_FOR_MTURK+"tasks/"+session.task_def.name+".xml")

        
        return url    


    def on_submit(self,submission):
        return None


    def on_deactivate(self,submission):
        return None

    def get_submission_xml(self,submission):
        return self.get_submission_xml_doc(submission).toxml();

    def get_submission_xml_doc(self,submission):
        session_code=submission.hit.session.code;
	GET,POST=submission.get_response();
        answer=POST['answer'];
        answer=answer.split(',');

        parameters= minidom.parseString(submission.hit.parameters);
                                    
        images=parameters.getElementsByTagName("img");

        x_doc=minidom.Document();
        x_root = x_doc.createElement("groups")
        x_doc.appendChild(x_root);
        for (i,a) in enumerate(answer):
            x_info = x_doc.createElement("img")
            x_root.appendChild(x_info);
            x_info.setAttribute("id",str(i+1));
            x_info.setAttribute("group",a);
            x_info.setAttribute("url",images[i].getAttribute("src"));

        print answer
        print x_doc.toxml()
        return x_doc
