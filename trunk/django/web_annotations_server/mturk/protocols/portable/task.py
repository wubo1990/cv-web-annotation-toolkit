import random,math,urllib,os,sys
from django.conf import settings
from django.shortcuts import get_object_or_404 

from datastore import xmlmisc
from xml.dom import minidom
from mturk.protocols.task import TaskEngine
import cPickle as pickler

try:
    import json
except ImportError:
    import simplejson as json 


class PortableTaskEngine(TaskEngine):
    def get_internal_params(self):
        return {'list_num_per_page':10,
                'frame_w':800,'frame_h':400};


    def get_base_url(self,task):
        params=self.reinterpret_task_parameters(task);
        return params["page_src"]+"?"


    def get_thumbnail_url(self,submission):
        return self.get_submission_view_url(submission)

    def get_submission_view_url(self,submission):
        hit=submission.hit;
        session=hit.session;

        url=self.get_base_url(session.task_def)

        url=url+"mode=display";

        url=url+"&instructionsUrl="+urllib.quote(session.task_def.instructions_url);

        hit_parameters_url=settings.HOST_NAME_FOR_MTURK+"mt/hit_parameters/"+hit.ext_hitid+"/";
        url=url+"&workUnitUrl="+urllib.quote(hit_parameters_url);
        url=url+"&submissionUrl="+urllib.quote(submission.get_persistent_url3());
        url=url+"&parametersUrl="+urllib.quote(settings.HOST_NAME_FOR_MTURK+"tasks/"+session.task_def.name+".xml")

        return url


    def get_grading_view_url(self,submission):
        return self.get_submission_view_url(submission)


    def reinterpret_task_parameters(self,task):
        parameters=json.loads(task.interface_xml)
        return parameters



    def get_task_page_url(self,task,request):
        session=task.session;

        url=self.get_base_url(session.task_def)

        url=url+"&mode=input";
        url=url+"&instructionsUrl="+urllib.quote(session.task_def.instructions_url);
        hit_parameters_url=settings.HOST_NAME_FOR_MTURK+"mt/hit_parameters/"+task.ext_hitid+"/";
        url=url+"&workUnitUrl="+urllib.quote(hit_parameters_url);
        url=url+"&parametersUrl="+urllib.quote(settings.HOST_NAME_FOR_MTURK+"tasks/"+session.task_def.name+".xml")
        url=url+"&submit=/mt/submit/";

        url=url+"&passthrough=extid";
        url=url+"&extid="+task.ext_hitid;

        return url    

    def on_submit(self,submission):
        return None


    def on_deactivate(self,submission):
        return None

    def get_submission_xml(self,submission):

	GET,POST=submission.get_response();

        attributes={};
        for k,v in POST.items():
            attributes[k]=v

        return json.dumps(attributes)

        #s=self.get_submission_xml_doc(submission).toxml();
        #return s



    def get_submission_xml_doc(self,submission):
        task_prototype_parameters = minidom.parseString(submission.session.task_def.interface_xml);
        work_unit_parameters = minidom.parseString(submission.hit.parameters);
        
        session_code=submission.hit.session.code;
	GET,POST=submission.get_response();

        x_doc=minidom.Document();
        x_root = x_doc.createElement("submission")
        attributes={};
        for k,v in POST.items():
            x_obj = x_doc.createElement(k)
            x_root.appendChild(x_obj);
            x_txt = x_doc.createTextNode(v);
            x_obj.appendChild(x_txt)

        x_doc.appendChild(x_root);

        #reference data
        x_root.setAttribute("ref-session",str(submission.session.code));
        x_root.setAttribute("ref-hit",submission.hit.ext_hitid);
        x_root.setAttribute("ref-worker",submission.worker);
        x_root.setAttribute("ref-submission",str(submission.id));

        return x_doc

