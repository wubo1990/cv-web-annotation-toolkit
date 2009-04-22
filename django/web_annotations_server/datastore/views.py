# Create your views here.

from django.http import HttpResponse,Http404
from django.conf import settings
from django.shortcuts import render_to_response,get_object_or_404 
from django.views.generic.list_detail import object_list
from django.views.generic.simple import redirect_to
from datastore.models import *
from django.contrib.auth.decorators import login_required

import os,urllib

def save_segmentation(request,segmentation_id):
	print "Save segmentation"
	print segmentation_id;
	image=request.POST['V']
	print len(image)
	outF=open(os.path.join(settings.SEGMENTATION_ROOT,segmentation_id),'wb')
	outF.write(image);
	outF.close();

	return HttpResponse("Done")

def load_segmentation(request,segmentation_id):
	print "Load segmentation"
	print segmentation_id;
	filename=os.path.join(settings.SEGMENTATION_ROOT,segmentation_id);
	if not os.path.exists(filename):
		raise Http404

	outF=open(filename,'rb');
	content=outF.read();
	outF.close();
	print content
	return HttpResponse(content,mimetype="text/plain")


@login_required
def register_images(request,dataset_name):
	if not request.user.has_perm('datastore.dataitem.add'):
		return HttpResponse('You are not authorized to add data items')

	dataset_path=os.path.join(settings.DATASETS_ROOT,dataset_name);
	dataset=get_object_or_404(Dataset,name=dataset_name);
	if len(dataset.dataitem_set.all())>0:
		return HttpResponse("Err: non-empty dataset");

	for fn in os.listdir(dataset_path):
		di=DataItem(url="/frames/"+dataset_name+"/"+fn,ds=dataset,type="image");
		di.save();

	return HttpResponse("Done");


def load_annotation(request,annotation_id):
	a=Annotation.objects.get(id=annotation_id);
	return HttpResponse(a.data);

def save_annotation(request,data_item_ref,ann_type,annotation_data):
	return HttpResponse("not implemented");

def show_data_items(request,dataset_name,page=None):
	if not page:
		return redirect_to(request,"p1/");

	ds = get_object_or_404(Dataset,name=dataset_name)
    	results=ds.dataitem_set.all();
	return object_list(request,queryset=results, paginate_by=20, page=page,
			template_name='datastore/dataitem_list.html');


def show_data_item(request,item_id):
	di = get_object_or_404(DataItem,id=item_id);
	types=AnnotationType.objects.all();
	ann_types=map(lambda t:t.name,types);

	empty_ann_types={};
	for t in types:
		empty_ann_types[t.name]=t;
		
	types_dict={};
	for t in di.annotation_set.all():
		#print t,t.rel_reference.all().count(),t.annotation_type.name,
		#for r in t.rel_reference.all():
		#	print r.annotation_type.name,
		#print ""
		if t.rel_reference.all().count()>0:
			continue
		if t.annotation_type.name not in types_dict:
			types_dict[t.annotation_type.name]=[t]
			del empty_ann_types[t.annotation_type.name]
		else:
			types_dict[t.annotation_type.name].append(t)
	di.by_type=types_dict;
	return render_to_response('datastore/dataitem.html',
				  {'object':di,'ann_types':ann_types,'empty_annotation_types':empty_ann_types.items() });

def get_annotation(request,item_id):
	ann = get_object_or_404(Annotation,id=item_id);
	return HttpResponse(ann.data);

@login_required
def new_annotation(request,item_id,annotation_type):
	if not request.user.has_perm('datastore.annotation.add'):
		return HttpResponse('You are not authorized to add annotation')

	ann_type = get_object_or_404(AnnotationType,name=annotation_type);
	data_item = get_object_or_404(DataItem,id=item_id);

	if request.method=="POST":
		print request.POST
		if "sites" in request.POST:
			val=request.POST["sites"]
			val="<?xml version='1.0'?>\n"+urllib.unquote(val);
			print val
		elif "annotation_value" in request.POST:
			val= request.POST["annotation_value"]
		elif "av_fields" in request.POST:
			fnames= request.POST["av_fields"]
			val=""
			for fn in fnames.split(","):
				if val:
					val=val+"&"+fn+"="+request.POST[fn];
				else:
					val=fn+"="+request.POST[fn];
		print val
		annotation=Annotation(ref_data=data_item,annotation_type=ann_type,author=request.user,data=val);
		annotation.save();
		return redirect_to(request,"../../../dataitem/%s"% data_item.id,permanent=False);
	else:
		return render_to_response('datastore/annotate_internal_'+ann_type.category+'.html',
					  {'object':data_item,'ann_type':ann_type });



@login_required
def new_related_annotation(request,item_id,ref_annotation_id,new_annotation_type):
	if not request.user.has_perm('datastore.annotation.add'):
		return HttpResponse('You are not authorized to add annotation')

	ann_type = get_object_or_404(AnnotationType,name=new_annotation_type);
	data_item = get_object_or_404(DataItem,id=item_id);
	ref_ann = get_object_or_404(Annotation,id=ref_annotation_id);

	if request.method=="POST":
		if "sites" in request.POST:
			val=request.POST["sites"]
		elif "annotation_value" in request.POST:
			val= request.POST["annotation_value"]
		elif "av_fields" in request.POST:
			fnames= request.POST["av_fields"]
			val=""
			for fn in fnames.split(","):
				if val:
					val=val+"&"+fn+"="+request.POST[fn];
				else:
					val=fn+"="+request.POST[fn];
			
		print val
		annotation=Annotation(ref_data=data_item,annotation_type=ann_type,author=request.user,data=val);
		annotation.save();
		annotation.rel_reference.add(ref_ann);
		annotation.save();

		return redirect_to(request,"../../../../../../dataitem/%s"% data_item.id,permanent=False);
	else:
		return render_to_response('datastore/annotate_internal_'+ann_type.category+'.html',
					  {'object':data_item,'ann_type':ann_type, 'ref_annotation':ref_ann });

