import random,math,urllib,os,sys
from django.conf import settings
from django.shortcuts import get_object_or_404 

from datastore import xmlmisc
from xml.dom import minidom
from mturk.protocols.task import TaskEngine
import cPickle as pickler

class AnyHTMLTaskEngine(TaskEngine):
    def get_internal_params(self):
        return {'list_num_per_page':10,
                'frame_w':800,'frame_h':400};


    def get_base_url(self,task):
        params=self.reinterpret_task_parameters(task);
        print params
        return params["page_src"]+"?"


    def get_thumbnail_url(self,submission):
        return self.get_submission_view_url(submission)

    def get_submission_view_url(self,submission):
        hit=submission.hit;
        session=hit.session;
        print "HP",session.task_def

        url=self.get_base_url(session.task_def)

        url=url+"mode=display";

        url=url+"&extid="+hit.ext_hitid;

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
        page_node=xmlmisc.xget(xmlObj,"page")[0];
        page_src=xmlmisc.xget_a(page_node,"src")
        print page_src
        print page_node

        return {'page_src':page_src}

    def get_models(self):
        print sys.modules.keys()
        return sys.modules["web_annotations_server.mturk.models"]


    def get_task_page_url(self,task,request):
        session=task.session;

        url=self.get_base_url(session.task_def)

        url=url+"&extid="+task.ext_hitid;

        url=url+"&mode=input";
        url=url+"&instructions="+urllib.quote(session.task_def.instructions_url);
        hit_parameters_url=settings.HOST_NAME_FOR_MTURK+"mt/hit_parameters/"+task.ext_hitid+"/";
        url=url+"&data_url="+urllib.quote(hit_parameters_url);
        url=url+"&parameters_url="+urllib.quote(settings.HOST_NAME_FOR_MTURK+"tasks/"+session.task_def.name+".xml")

        url=url+"&submit_parameters_url="+urllib.quote(settings.HOST_NAME_FOR_MTURK+"tasks/"+session.task_def.name+".xml")

        url=url+"&submit_url=/mt/submit/";
        return url    


    def on_submit(self,submission):
        return None


    def on_deactivate(self,submission):
        return None

    def get_submission_xml(self,submission):
        s=self.get_submission_xml_doc(submission).toxml();
        return s

    def get_submission_xml_doc(self,submission):
        task_prototype_parameters = minidom.parseString(submission.session.task_def.interface_xml);
        work_unit_parameters = minidom.parseString(submission.hit.parameters);
        
        session_code=submission.hit.session.code;
	GET,POST=submission.get_response();
        print GET,POST

        attributes={};
        for k,v in POST.items():
            if k.startswith("A_"):
                attributes[k]=v;

        comment=POST.get("Comments",None);
        
        x_doc=minidom.Document();

        x_root = x_doc.createElement("submission")
        x_doc.appendChild(x_root);

        #reference data
        x_root.setAttribute("ref-session",str(submission.session.code));
        x_root.setAttribute("ref-hit",submission.hit.ext_hitid);
        x_root.setAttribute("ref-submission",str(submission.id));

        #comment if available
        if(comment):
            x_obj = x_doc.createElement("comments")
            x_root.appendChild(x_obj);
            x_obj.setAttribute("text",comment);


        #object_attributes;
        id=0;
        for (a,v) in attributes.items():
            x_obj = x_doc.createElement("attribute")
            x_root.appendChild(x_obj);
            id+=1
            x_obj.setAttribute("id",str(id));
            x_obj.setAttribute("tgt",a.replace("A_",""));
            x_obj.setAttribute("value",v);
        return x_doc

