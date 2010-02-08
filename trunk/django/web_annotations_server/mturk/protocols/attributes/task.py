import random,math,urllib,os,sys
from django.conf import settings
from django.shortcuts import get_object_or_404 

from datastore import xmlmisc
from xml.dom import minidom
from mturk.protocols.task import TaskEngine
import cPickle as pickler

class AttributesTaskEngine(TaskEngine):
    """ This task determines a collection of attributes for each item."""


    def get_internal_params(self):
        return {'list_num_per_page':3,
                'frame_w':1200,'frame_h':1500};


    def get_base_url(self):
        """HTML file implementing the interface"""
        return "/code/attributes_grid.html?"


    def get_thumbnail_url(self,submission):
        return self.get_submission_view_url(submission)

    def get_submission_view_url(self,submission):
        """How to form a submission URL"""

        hit=submission.hit;
        session=hit.session;

        url=self.get_base_url()

        url=url+"mode=display";
        url=url+"&extid="+hit.ext_hitid;

        url=url+"&session="+session.code;

        url=url+"&task="+session.task_def.name

        url=url+"&video="+session.code;
        url=url+"&video_mode=play";
        url=url+"&img_base="+settings.HOST_NAME_FOR_MTURK;
        url=url+"&instructions="+urllib.quote(session.task_def.instructions_url);

        hit_parameters_url=settings.HOST_NAME_FOR_MTURK+"mt/hit_parameters/"+hit.ext_hitid+"/";
        url=url+"&data_url="+urllib.quote(hit_parameters_url);

        url=url+"&annotation_url="+urllib.quote(submission.get_persistent_url2());
        url=url+"&parameters_url="+urllib.quote(settings.HOST_NAME_FOR_MTURK+"tasks/"+session.task_def.name+".xml")

        return url


    def get_grading_view_url(self,submission,grading_parameters={}):
        return self.get_submission_view_url(submission)


    def reinterpret_task_parameters(self,task):
        xmlObj=task.parse_parameters_xml();

        return {} 

    def get_task_page_url(self,task,request):
        session=task.session;

        url=self.get_base_url()

        url=url+"&extid="+task.ext_hitid;

        url=url+"&session="+session.code;

        url=url+"&task="+session.task_def.name

        url=url+"&video="+session.code;
        url=url+"&video_mode=play";
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

        task_prototype_parameters = minidom.parseString(submission.session.task_def.interface_xml);
        work_unit_parameters = minidom.parseString(submission.hit.parameters);
        

        attributes = xmlmisc.xfetch_attributes(task_prototype_parameters,'attributes','attribute','id');
        items = xmlmisc.xfetch_attributes(work_unit_parameters,'items','item','id');

        x_doc=minidom.Document();

        object_attributes={};
    
        session_code=submission.hit.session.code;
	GET,POST=submission.get_response();
        print GET,POST

        valid_attributes={};
        for i in items:
            for a in attributes:
               valid_attributes ['A_obj%s_%s' % (i,a)]=(i,a)

        for k,v in POST.items():
            if k.startswith("A_"):
                assert( k in valid_attributes );

                objID,attr_name = valid_attributes[k];

                if objID not in object_attributes:
                    object_attributes[objID]={};

                object_attributes[objID][attr_name]=v;
        comment=POST.get("Comments",None);
        
        #object_attributes;
        x_root = x_doc.createElement("objects")
        x_root.setAttribute("ref-session",str(submission.session.code));
        x_root.setAttribute("ref-hit",submission.hit.ext_hitid);
        x_root.setAttribute("ref-submission",str(submission.id));
        x_root.setAttribute("id",str(submission.id));

        if(comment):
            x_obj = x_doc.createElement("comments")
            x_obj.setAttribute("text",comment);
            x_root.appendChild(x_obj);

        x_doc.appendChild(x_root);
        for (obj,attrs) in object_attributes.items():
            x_obj = x_doc.createElement("object")
            x_obj.setAttribute("id",obj);
            x_root.appendChild(x_obj);
            for attr_name,attr_value in attrs.items():
                x_obj.setAttribute(attr_name,attr_value);
                #x_attr = x_doc.createElement("attribute")
                #x_attr.setAttribute("name",attr_name);
                #x_attr.setAttribute("value",attr_value);


        return x_doc

