
import shutil,os,sys,subprocess

from django.http import Http404,HttpResponse,HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response,get_object_or_404
from django.core.files.storage import FileSystemStorage
from forms import *
from django.views.generic.simple import redirect_to
from django.conf import settings
import uuid,tempfile
from time import strftime

from PIL import Image

import mturk.models
import mturk.views




def do_post(request,session,form):
	return HttpResponse("done");

	user = request.user;
        print form.cleaned_data
	print uploaded_file
        submission_rt=os.path.join(settings.DATASETS_ROOT,session.code);

        id = session.mthit_set.count()+1;
	rand_id=str(uuid.uuid4())+"-"+str(id)
	print dir(uploaded_file)
	original_name =uploaded_file.name
        storage = FileSystemStorage(submission_rt);
        fname=storage.save(os.path.join(submission_rt,rand_id+".jpg"),uploaded_file);

	params="image_url=/frames/"+session.code+"/"+rand_id+".jpg&frame="+rand_id+"&original_name="+original_name 
	print params
        hit=mturk.models.MTHit(session=session,ext_hitid=rand_id,int_hitid=id,parameters=params);
	hit.save();
	if form.cleaned_data["submit_for_annotation"]:
		(activated,msg)=mturk.views.activate_hit(session,hit);
	else:
		activated=False
		msg="submission disabled"

	return HttpResponse("done. Activated %d, %s" % (activated,msg))


def submit_boxes_to_attributes(request):
    if request.method == 'POST':
        form = PostBoxesToAttributesForm(request.POST, request.FILES)
        if form.is_valid():
            return do_post(request,session,form);
    else:
        form = PostBoxesToAttributesForm()

    return render_to_response('protocols/attributes/post_boxes_to_attributes.html', {'form': form,'user':request.user})


def create_raw_xml_download(request,session_code):
    session = get_object_or_404(mturk.models.Session,code=session_code)
    download_rt=os.path.join(settings.DATASETS_ROOT,'downloads',session.code,'raw_xml');
    if not os.path.exists(download_rt):
        os.makedirs(download_rt);	

    timeid=strftime("%d-%b-%Y-%H-%M-%S")
    save_dir=os.path.join(download_rt,timeid,session.code);

    proc=subprocess.Popen("/var/django/session_xml_results.sh --session=%s --server=%s --saveto=%s/%s/%s/" % (session.code,settings.SITE_NAME,download_rt,timeid,session.code), shell=True,env={})
    proc.communicate();

    os.system("tar cvzCf %s/%s/ %s/%s-%s-raw_xml.tgz %s"%(download_rt,timeid,download_rt,session.code,timeid,session.code))

    return HttpResponseRedirect("/mt/download/"+session.code+"/raw_xml/"+session.code+"-"+timeid+"-raw_xml.tgz")

