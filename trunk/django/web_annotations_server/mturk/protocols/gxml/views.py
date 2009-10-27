# Create your views here.

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


@login_required
def upload_image(request,session_code):
	session = get_object_or_404(mturk.models.Session,code=session_code)
	#if not request.user.has_perm('datastore.evaluation.add'):
	#	return render_to_response('registration/not_authorized.html')


	if request.method == 'POST':
		form = UploadImageForm(request.POST, request.FILES)
		if form.is_valid():
			uploaded_file=request.FILES['image_file'];
			return do_upload_image(request,session,form,uploaded_file);
	else:
		form = UploadImageForm()
	return render_to_response('protocols/gxml/upload_image.html', {'form': form,'user':request.user})







def do_upload_image(request,session,form,uploaded_file):
	
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
		(activated,id)=mturk.views.activate_hit(session,hit);
	else:
		activated=False

	return HttpResponse("done. Activated %d" % activated)




@login_required
def upload_image_tgz(request,session_code):
	session = get_object_or_404(mturk.models.Session,code=session_code)
	#if not request.user.has_perm('datastore.evaluation.add'):
	#	return render_to_response('registration/not_authorized.html')


	if request.method == 'POST':
		form = UploadImageTGZForm(request.POST, request.FILES)
		if form.is_valid():
			uploaded_file=request.FILES['image_tgz_file'];
			return do_upload_image_tgz(request,session,form,uploaded_file);
	else:
		form = UploadImageTGZForm()
	return render_to_response('protocols/gxml/upload_image_tgz.html', {'form': form,'user':request.user})



def do_upload_image_tgz(request,session,form,uploaded_file):
	
	user = request.user;
        print form.cleaned_data
	print uploaded_file
        upload_rt=os.path.join(settings.DATASETS_ROOT,'uploads',session.code);
        session_image_dir=os.path.join(settings.DATASETS_ROOT,session.code);
	if not os.path.exists(upload_rt):
		os.makedirs(upload_rt);

	if not os.path.exists(session_image_dir):
		os.makedirs(session_image_dir);

	upload_dir=tempfile.mktemp(dir=upload_rt);

        submission_rt=os.path.join(settings.DATASETS_ROOT,session.code);
	#print dir(uploaded_file)
	original_name =uploaded_file.name
        storage = FileSystemStorage(upload_dir);
        fname=storage.save(None,uploaded_file);

	if fname.find(' ') >-1 or fname.find("'")>-1 or fname.find('"')>-1:
		needToFixFilename=True
	else:
		needToFixFilename=False

	if needToFixFilename:
		print "WARNING: space or quote found in the submission file name. Please avoid spaces and quotes in submission file name",fname;
		fixed_filename=fname.replace(' ','_').replace("'","_").replace('"','_');
		shutil.move(os.path.join(upload_dir,fname),os.path.join(upload_dir,fixed_filename));
		fname=fixed_filename;
        status=os.system("tar xvzCf %s %s" % (upload_dir,os.path.join(upload_dir,fname)));

	dirs=filter(lambda s: s <> fname, os.listdir(upload_dir))
	print fname,dirs
	if len(dirs) <> 1:
		return HttpResponse("Error: more than 1 folder in the tgz file");

	image_folder=dirs[0]
	image_names=filter(lambda s: s.endswith('.jpg') or s.endswith('.JPG'),os.listdir(os.path.join(upload_dir,image_folder)))

	nAdded=0;
	nActivated=0;

	id = session.mthit_set.count();
	for img_name in  image_names:
		id += 1;
		rand_id=str(uuid.uuid4())+"-"+str(id)

		shutil.copyfile(os.path.join(upload_dir,image_folder,img_name),
				os.path.join(session_image_dir,rand_id+".jpg"));

		original_name = img_name
		params="image_url=/frames/"+session.code+"/"+rand_id+".jpg&frame="+rand_id+"&original_name="+original_name 
		print params
		hit=mturk.models.MTHit(session=session,ext_hitid=rand_id,int_hitid=id,parameters=params);
		hit.save();
		nAdded+=1;
		if form.cleaned_data["submit_for_annotation"]:
			(activated,hitid)=mturk.views.activate_hit(session,hit);
			if activated:
				nActivated+=1;
		else:
			pass

	return HttpResponse("done. Added %d, Activated %d" % (nAdded,nActivated))


def create_full_pack_download(request,session_code):
	session = get_object_or_404(mturk.models.Session,code=session_code)
	download_rt=os.path.join(settings.DATASETS_ROOT,'downloads',session.code,'pack');
	if not os.path.exists(download_rt):
		os.makedirs(download_rt);	

	img_rt=os.path.join(settings.DATASETS_ROOT,session.code);
	fns=os.listdir(img_rt);
	if len(fns)==0:
		return HttpResponse("Failed. No images")
	fn=fns[0];
	im = Image.open(os.path.join(img_rt,fn));
	img_resolution = "%dx%d" % (im.size[0],im.size[1]);

	timeid=strftime("%d-%b-%Y-%H-%M-%S")
	#proc=subprocess.Popen("rosrun cv_mech_turk session_results.py --session=%s --server=%s --saveto=%s/%s/%s/; env" % (session.code,settings.SITE_NAME,download_rt,timeid,session.code),stdout=subprocess.PIPE, stderr=subprocess.PIPE,stdin=subprocess.PIPE, shell=True)

	#(stdoutdata, stderrdata)=proc.communicate("source /var/django2/ros.env; echo rosrun cv_mech_turk session_results.py --session=%s --server=%s --saveto=%s/%s/%s/; env" % (session.code,settings.SITE_NAME,download_rt,timeid,session.code));

	proc=subprocess.Popen("/var/django2/session_results.sh --session=%s --server=%s --saveto=%s/%s/%s/" % (session.code,settings.SITE_NAME,download_rt,timeid,session.code), shell=True,env={})
	proc.communicate();

	proc=subprocess.Popen("/var/django2/session_results_masks.sh %s/%s/%s/ %s" % (download_rt,timeid,session.code,img_resolution),shell=True,env={})
	proc.communicate();

	os.system("tar cvzCf %s/%s/ %s/%s-%s-pack.tgz %s"%(download_rt,timeid,download_rt,session.code,timeid,session.code))

	return HttpResponseRedirect("/mt/download/"+session.code+"/pack/"+session.code+"-"+timeid+"-pack.tgz")
	#return HttpResponseRedirect("/mt/download/"+session.code+"/pack/"+session.code+"-"+timeid+".tgz")


def create_xml_masks_download(request,session_code):
	session = get_object_or_404(mturk.models.Session,code=session_code)
	download_rt=os.path.join(settings.DATASETS_ROOT,'downloads',session.code,'xml_and_masks');
	if not os.path.exists(download_rt):
		os.makedirs(download_rt);	

	img_rt=os.path.join(settings.DATASETS_ROOT,session.code);
	fns=os.listdir(img_rt);
	if len(fns)==0:
		return HttpResponse("Failed. No images")
	fn=fns[0];
	im = Image.open(os.path.join(img_rt,fn));
	img_resolution = "%dx%d" % (im.size[0],im.size[1]);

	timeid=strftime("%d-%b-%Y-%H-%M-%S")
	proc=subprocess.Popen("/var/django2/session_results.sh --session=%s --server=%s --saveto=%s/%s/%s/" % (session.code,settings.SITE_NAME,download_rt,timeid,session.code), shell=True,env={})
	proc.communicate();

	proc=subprocess.Popen("/var/django2/session_results_masks.sh %s/%s/%s/ %s" % (download_rt,timeid,session.code,img_resolution),shell=True,env={})
	proc.communicate();

	os.system("rm %s/%s/%s/images/*" % (download_rt,timeid,session.code))
	os.system("tar cvzCf %s/%s/ %s/%s-%s-xml_and_masks.tgz %s"%(download_rt,timeid,download_rt,session.code,timeid,session.code))

	return HttpResponseRedirect("/mt/download/"+session.code+"/xml_and_masks/"+session.code+"-"+timeid+"-xml_and_masks.tgz")
