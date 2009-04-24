# Create your views here.

from django.http import HttpResponse,Http404
from django.conf import settings
from django.shortcuts import render_to_response,get_object_or_404 
from django.views.generic.list_detail import object_list
from django.views.generic.simple import redirect_to
from datastore.models import *
from django.contrib.auth.decorators import login_required

import os,urllib
from xml.dom import minidom

try:
	try:
		import Image
	except:
		from PIL import Image
except:	
	Image=None



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



def register_images_recursive(dataset,base_dir,working_dir):
	for fn in os.listdir(os.path.join(base_dir,working_dir)):
		if os.path.isdir(os.path.join(base_dir,working_dir,fn)):
			register_images_recursive(dataset,base_dir,os.path.join(working_dir,fn))
		else:
			di=DataItem(url="/frames/"+dataset.name+"/"+working_dir+"/"+fn,ds=dataset,type="image");
			di.save();

@login_required
def register_images(request,dataset_name):
	if not request.user.has_perm('datastore.dataitem.add'):
		return render_to_response('registration/not_authorized.html')

	dataset_path=os.path.join(settings.DATASETS_ROOT,dataset_name);
	dataset=get_object_or_404(Dataset,name=dataset_name);
	if len(dataset.dataitem_set.all())>0:
		return HttpResponse("Err: non-empty dataset");

	register_images_recursive(dataset,dataset_path,'');

	return HttpResponse("Done");


def xget(o,tagname):
	return o.getElementsByTagName(tagname);
def xget_v(o,tagname):
	fc=o.getElementsByTagName(tagname)[0].firstChild
	if fc:
		return	fc.nodeValue;
	else:	
		return None
def xget_v2(o,tagnames):
	return map(lambda t:xget_v(o,t),tagnames);

@login_required
def register_voc_boxes(request,dataset_name):
	if not request.user.has_perm('datastore.annotation.add'):
		return render_to_response('registration/not_authorized.html')

	annotation_type="voc2008_boxes"
	ann_type = get_object_or_404(AnnotationType,name=annotation_type);

	dataset_path=os.path.join(settings.DATASETS_ROOT,dataset_name);
	annotation_path=os.path.join(settings.DATASETS_ROOT,dataset_name+"_annotations");
	dataset=get_object_or_404(Dataset,name=dataset_name);
	resp=HttpResponse();
	for dt_item in dataset.dataitem_set.all():
		#print dt_item.id,
		#print dt_item.url
		(str_img,str_img_path,str_img_file)=dt_item.get_name_parts();    
		
		#print str_img,str_img_path,str_img_file
		annotation_filename=os.path.join(annotation_path,str_img_file+".xml");
		if not os.path.exists(annotation_filename):
			resp.write("Missing annotations file for %s<br/>\n" % annotation_filename);

		full_annotation="""<?xml version='1.0'?>
<results>
<annotation>"""
		xmldoc = minidom.parse(annotation_filename);
		object_tags=xmldoc.getElementsByTagName("object");

		img_size=xget(xmldoc,"size")[0];
		img_w=float(xget_v(img_size,"width"));
		img_h=float(xget_v(img_size,"height"));
		scale=min(500/img_w,500/img_h);
		dX=(500-img_w*scale)/2;
		dY=(500-img_h*scale)/2;
		#print img_w,scale
		iSqn=1;
		for o in object_tags:
			object_name=xget_v(o,"name");
			bbox=xget(o,"bndbox")[0];
			(o_xmin,o_xmax,o_ymin,o_ymax)=xget_v2(bbox,["xmin","xmax","ymin","ymax"])
			xmin=float(o_xmin)*scale+dX;
			xmax=float(o_xmax)*scale+dX;
			ymin=float(o_ymin)*scale+dY;
			ymax=float(o_ymax)*scale+dY;
			w=xmax-xmin;
			h=ymax-ymin;
			object_xml="""<bbox2 name="%s" sqn="%d" >
<bbox name="%s" sqn="1" left="%s" top="%s" width="%d" height="%d">
<pt x="%s" y="%s" ct="0"/>
<pt x="%s" y="%s" ct="0"/>
</bbox>
</bbox2>""" % (object_name, iSqn, object_name, xmin,ymin,w,h,xmin,ymin,xmax,ymax)
			iSqn = iSqn+1;
			full_annotation+=object_xml

		full_annotation+="</annotation></results>"
		#print full_annotation
		annotation=Annotation(ref_data=dt_item,annotation_type=ann_type,author=request.user,data=full_annotation);
		annotation.save();
		#return resp

			     
	resp.write("done");
	return resp


@login_required
def register_labelme_boxes(request,dataset_name):
	if not request.user.has_perm('datastore.annotation.add'):
		return render_to_response('registration/not_authorized.html')

	annotation_type="labelme_boxes"
	ann_type = get_object_or_404(AnnotationType,name=annotation_type);

	if not Image:
		return HttpResponse("Error. Server installation of python Image library is missing");


	dataset_path=os.path.join(settings.DATASETS_ROOT,dataset_name);
	annotation_path=os.path.join(settings.DATASETS_ROOT,dataset_name+"_annotations");
	dataset=get_object_or_404(Dataset,name=dataset_name);
	resp=HttpResponse();
	for dt_item in dataset.dataitem_set.all():
		#print dt_item.id,
		#print dt_item.url
		(str_img,str_img_path,str_img_file)=dt_item.get_name_parts();    
		
		#print str_img,str_img_path,str_img_file
		annotation_filename=os.path.join(annotation_path,str_img_path,str_img_file+".xml");
		if not os.path.exists(annotation_filename):
			resp.write("Missing annotations file for %s<br/>\n" % annotation_filename);

		full_annotation="""<?xml version='1.0'?>
<results>
<annotation>"""
		xmldoc = minidom.parse(annotation_filename);
		object_tags=xget(xmldoc,"object");
		image_filename=os.path.join(dataset_path,str_img_path,str_img_file+".jpg");
		print image_filename
		#im = imread(image_filename);
		im = Image.open(image_filename);
		(img_w,img_h) = im.size;
		scale=min(500.0/img_w,500.0/img_h);
		dX=(500-img_w*scale)/2;
		dY=(500-img_h*scale)/2;
		iSqn=1;
		
		for o in object_tags:
			object_name = xget_v(o,"name")
			if not object_name:
				continue
			polygon=xget(o,"polygon")[0];
			points=xget(polygon,"pt");
			points_new=[];
			for pt in points:
				x=float(xget_v(pt,"x"))
				y=float(xget_v(pt,"y"))
				points_new.append([x,y]);
			(o_xmin,o_ymin)=reduce(lambda (x,y),(x2,y2):(min(x,x2),min(y,y2)),points_new);
			(o_xmax,o_ymax)=reduce(lambda (x,y),(x2,y2):(max(x,x2),max(y,y2)),points_new);
			print object_name, o_xmin,o_ymin, o_xmax,o_ymax

			xmin=float(o_xmin)*scale+dX;
			xmax=float(o_xmax)*scale+dX;
			ymin=float(o_ymin)*scale+dY;
			ymax=float(o_ymax)*scale+dY;
			w=xmax-xmin;
			h=ymax-ymin;
			object_xml="""<bbox2 name="%s" sqn="%d" >
<bbox name="%s" sqn="1" left="%s" top="%s" width="%d" height="%d">
<pt x="%s" y="%s" ct="0"/>
<pt x="%s" y="%s" ct="0"/>
</bbox>
</bbox2>""" % (object_name, iSqn, object_name, xmin,ymin,w,h,xmin,ymin,xmax,ymax)
			iSqn = iSqn+1;
			full_annotation+=object_xml

		full_annotation+="</annotation></results>"
		#print full_annotation
		annotation=Annotation(ref_data=dt_item,annotation_type=ann_type,author=request.user,data=full_annotation);
		annotation.save();
			     
	resp.write("Done importing LabelMe annotations as boxes");
	return resp



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


def show_dataset_annotations(request,dataset_name,annotation_type,page=None):
	if not page:
		return redirect_to(request,"p1/");

	ds = get_object_or_404(Dataset,name=dataset_name)
	ann_type = get_object_or_404(AnnotationType,name=annotation_type)

	results=ann_type.annotation_set.filter(ref_data__ds__id=ds.id).filter(is_active=True);
	print results,page
	return object_list(request,queryset=results, paginate_by=20, page=page,
			template_name='datastore/annotation_list.html');


def show_flagged_annotations(request,dataset_name,annotation_type,flag_name,page=None):
	if not page:
		return redirect_to(request,"p1/");

	ds = get_object_or_404(Dataset,name=dataset_name)
	ann_type = get_object_or_404(AnnotationType,name=annotation_type)
	flag_ann_type = get_object_or_404(AnnotationType,name="flags")

	#flag_ann_type.annotation_set.reannotation
	print flag_ann_type.id
	#results=Annotation.objects.filter(annotation__annotation_type=flag_ann_type);
	results=Annotation.objects.filter(data=flag_name,annotation_type__id=flag_ann_type.id,ref_data__ds__id=ds.id,is_active=True) ; #15722)
	#results=ann_type.annotation_set.filter(ref_data__ds__id=ds.id).filter(is_active=True);
	print results,page
	return object_list(request,queryset=results, paginate_by=20, page=page,
			template_name='datastore/annotation_list2.html');


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
		return render_to_response('registration/not_authorized.html')

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
def flag_annotation(request,annotation_id,flag):
	if not request.user.has_perm('datastore.annotation.add'):
		return render_to_response('registration/not_authorized.html')

	ann_type = get_object_or_404(AnnotationType,name="flags");
	ref_annotation = get_object_or_404(Annotation,id=annotation_id);

	annotation=Annotation(ref_data=ref_annotation.ref_data,annotation_type=ann_type,author=request.user,data=flag);
	annotation.save();
	annotation.rel_reference.add(ref_annotation);
	annotation.save();
	return render_to_response('datastore/flag.html')


def show_annotation(request,item_id):
	ann = get_object_or_404(Annotation,id=item_id);
	di = ann.ref_data;
	return render_to_response('datastore/show_annotation.html',
				  {'object':ann, 'ref_data':di});


@login_required
def new_related_annotation(request,ref_annotation_id,new_annotation_type,item_id=None,depth={}):
	if not request.user.has_perm('datastore.annotation.add'):
		return HttpResponse('You are not authorized to add annotation')

	#if 'depth' in extra_args:
	#	depth=extra_args['depth'];
	#else:
	#	depth=2

	ann_type = get_object_or_404(AnnotationType,name=new_annotation_type);
	ref_ann = get_object_or_404(Annotation,id=ref_annotation_id);
	if item_id:
		data_item = get_object_or_404(DataItem,id=item_id);
	else:
		data_item = ref_ann.ref_data

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

		#return redirect_to(request,"../../../../../../dataitem/%s"% data_item.id,permanent=False);
		s="";
		for i in range(0,depth):
			s=s+"../";
		return redirect_to(request,s,permanent=False);
	else:
		return render_to_response('datastore/annotate_internal_'+ann_type.category+'.html',
					  {'object':data_item,'ann_type':ann_type, 'ref_annotation':ref_ann });

