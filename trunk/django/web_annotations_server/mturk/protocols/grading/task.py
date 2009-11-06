import random,math,urllib,os,sys
from django.conf import settings
from django.shortcuts import get_object_or_404 

from datastore import xmlmisc
from xml.dom import minidom
from mturk.protocols.task import TaskEngine
import cPickle as pickler

class GradingTaskEngine(TaskEngine):
    def get_internal_params(self):
        return {'list_num_per_page':1,
                'frame_w':800,'frame_h':800};

    def get_submission_view_url(self,submission):
        hit=submission.hit;
        session=hit.session;

        url="/code/grading.html?"
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
        print url
        return url


    def get_grading_view_url(self,submission):
        return self.get_submission_view_url(submission)


    def reinterpret_task_parameters(self,task):
        xmlObj=task.parse_parameters_xml();
        sampling_node=xmlmisc.xget(xmlObj,"sampling")[0];
        overlap=float(xmlmisc.xget_a(sampling_node,"overlap"))

        layout_node=xmlmisc.xget(xmlObj,"layout")[0];
        num_per_task=int(xmlmisc.xget_a(layout_node,"num_per_task"));
        frame_w=int(xmlmisc.xget_a_d(layout_node,"frame_w","550"));
        frame_h=int(xmlmisc.xget_a_d(layout_node,"frame_h","500"));
        return {'overlap':overlap,'num_per_task':num_per_task,"frame_w":frame_w,"frame_h":frame_h};

    def get_models(self):
        print sys.modules.keys()
        return sys.modules["web_annotations_server.mturk.models"]


    def get_task_page_url(self,task,request):
        session=task.session;

        url="/code/grading.html?"

        url=url+"&extid="+task.ext_hitid;

        url=url+"&session="+session.code;

        url=url+"&task="+session.task_def.name

        url=url+"&video="+session.code;
        url=url+"&img_base="+settings.HOST_NAME_FOR_MTURK;
        url=url+"&mode=input";
        url=url+"&instructions="+urllib.quote(session.task_def.instructions_url);
        hit_parameters_url=settings.HOST_NAME_FOR_MTURK+"mt/hit_parameters/"+task.ext_hitid+"/";
        url=url+"&data_url="+urllib.quote(hit_parameters_url);
        
        return url    


    def on_submit(self,submission):
	GET,POST=submission.get_response();
        grading_id=submission.session.code+"/"+str(submission.id);
        grades={};
        feedback={};
        for (k,v) in POST.items():
            if k.startswith("quality__"):
                id=k.replace("quality__","");
                grades[id]=v;
            elif k.startswith("message__"):
                id=k.replace("message__","");
                feedback[id]=v;
        w,created=self.get_models().Worker.objects.get_or_create(session=None,worker=submission.worker);
        if created:
            w.save();

        for sub_id in grades.keys():
            (session_code,submission_id)=sub_id.split("_");

            session=get_object_or_404(self.get_models().Session,code=session_code)
            original_submission=get_object_or_404(self.get_models().SubmittedTask,id=submission_id)
            quality=int(grades[sub_id]);
            grade_record=self.get_models().ManualGradeRecord(submission=original_submission,
                                           quality=quality,
                                           feedback=feedback.get(k,""),
                                           worker=w,
                                           reference=grading_id);
            grade_record.save();
        pass;

    def on_deactivate(self,submission):
	GET,POST=submission.get_response();
        grades={};
        feedback={};
        for (k,v) in POST.items():
            if k.startswith("quality__"):
                id=k.replace("quality__","");
                grades[id]=v;
            elif k.startswith("message__"):
                id=k.replace("message__","");
                feedback[id]=v;

        w,created=self.get_models().Worker.objects.get_or_create(session=None,worker=submission.worker);
        if created:
            w.save();

        print "DEACTIVATE"
        for sub_id in grades.keys():
            (session_code,submission_id)=sub_id.split("_");

            session=get_object_or_404(self.get_models().Session,code=session_code)
            original_submission=get_object_or_404(self.get_models().SubmittedTask,id=submission_id)
            quality=int(grades[sub_id]);
            grades=self.get_models().ManualGradeRecord.objects.filter(
                submission=original_submission,
                quality=quality,
                worker=w);
            for grade_record in grades:
                grade_record.valid=False;
                grade_record.save();
        return None

    def get_submission_xml(self,submission):
        return self.get_submission_xml_doc(submission).toxml();

    def get_submission_xml_doc(self,submission):
        session_code=submission.hit.session.code;
	GET,POST=submission.get_response();
        grades={};
        feedback={};
        for (k,v) in POST.items():
            if k.startswith("quality__"):
                id=k.replace("quality__","");
                grades[id]=v;
            elif k.startswith("message_"):
                id=k.replace("message_","");
                feedback[id]=v;

        print feedback
        x_doc=minidom.Document();
        x_root = x_doc.createElement("grades")
        x_doc.appendChild(x_root);
        x_info = x_doc.createElement("info")
        x_root.appendChild(x_info);
        x_info.setAttribute("for_session",session_code);
        x_info.setAttribute("by_worker",submission.worker);

        for sub_id in grades.keys():
            (session_code,submission_id)=sub_id.split("_");
            x_grade = x_doc.createElement("grade")
            x_root.appendChild(x_grade);
            x_grade.setAttribute("for_session",session_code);
            x_grade.setAttribute("for_id",submission_id);
            x_grade.setAttribute("grade",grades[sub_id]);
            if sub_id in feedback:
                x_grade.setAttribute("feedback",feedback[sub_id]);
            x_grade.setAttribute("by_worker",submission.worker);

        return x_doc
