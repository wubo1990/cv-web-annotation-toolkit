# Create your views here.
# -*- coding: UTF-8 -*-

from django.http import HttpResponse,Http404,HttpResponseRedirect
from django.conf import settings
from django.shortcuts import render_to_response,get_object_or_404 
from django.views.generic.list_detail import object_list
from django.views.generic.simple import redirect_to
from datastore.models import *
from django.contrib.auth.decorators import login_required
from django.utils.encoding import *
from forms import *
import tagging.models

import os,sys,time,urllib,mimetools,datetime,random
import zlib,array,struct

import StringIO
from xml.dom import minidom
from xmlmisc import *




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
	return HttpResponse(content,mimetype="text/plain")


def txt2bin(txt):
    a=array.array('B')
    m={'A':0,'B':1,'C':2,'D':3,'E':4,'F':5,'G':6,'H':7,'I':8,'J':9,'K':10,'L':11,'M':12,'N':13,'O':14,'P':15};

    for i in range(0,len(txt),2):
        c=txt[i];
        c2=txt[i+1];
        v=m[c]*16+m[c2]
        a.append(v)
    return a;

def get_segmentation_img(request,segmentation_id):
	print segmentation_id;
	filename=os.path.join(settings.SEGMENTATION_ROOT,segmentation_id);
	if not os.path.exists(filename):
		raise Http404

	outF=open(filename,'rb');
	content=outF.read();
	outF.close();

	binary_txt=txt2bin(content);
	header=binary_txt[0:32];
	(w,h)=struct.unpack("!ii",header[0:8])
	pixels=array.array('b',zlib.decompress(binary_txt[32:]));
	print header,w,h
	for i in xrange(0,len(pixels),4):
		a=pixels[i];
		pixels[i]=pixels[i+1];
		pixels[i+1]=pixels[i+2];
		pixels[i+2]=pixels[i+3];
		pixels[i+3]=a;
	im = Image.frombuffer("RGBA", (w,h), pixels);
	response = HttpResponse(mimetype="image/png")
	im.save(response, "PNG")
	return response

	im = Image.open(image_filename);	

	return response	


def get_wnd(request,item_id,l,t,w,h):

	data_item=get_object_or_404(DataItem,id=item_id);
	(str_img,str_img_path,str_img_file)=data_item.get_name_parts();    

	dataset_path=os.path.join(settings.DATASETS_ROOT,data_item.ds.name);
	image_filename=os.path.join(dataset_path,str_img_path,str_img_file+".jpg");
	im = Image.open(image_filename);	

	c = im.crop(map(lambda v:int(round(v)),[float(l),float(t),float(l)+float(w),float(t)+float(h)]));
	response = HttpResponse(mimetype="image/jpeg")
	c.save(response, "JPEG")

	return response

def get_wnd2(request,item_name,l,t,w,h):

	image_filename=os.path.join(settings.DATASETS_ROOT,item_name);
	if not os.path.exists(image_filename):
		raise Http404();
	im = Image.open(image_filename);	

	c = im.crop(map(lambda v:int(round(v)),[float(l),float(t),float(l)+float(w),float(t)+float(h)]));
	response = HttpResponse(mimetype="image/jpeg")
	c.save(response, "JPEG")

	return response



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





@login_required
def register_voc_boxes(request,dataset_name):
	if not request.user.has_perm('datastore.annotation.add'):
		return render_to_response('registration/not_authorized.html')

	annotation_type="voc2008_boxes"
	ann_type = get_object_or_404(AnnotationType,name=annotation_type);

        TM=tagging.models.Tag.objects;
        tag_name="Source-Annotation";

	dataset_path=os.path.join(settings.DATASETS_ROOT,dataset_name);
	annotation_path=os.path.join(settings.DATASETS_ROOT,dataset_name+"_annotations");
	dataset=get_object_or_404(Dataset,name=dataset_name);
	resp=HttpResponse();
	for dt_item in dataset.dataitem_set.all():
		(str_img,str_img_path,str_img_file)=dt_item.get_name_parts();    
		
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
		img_d=float(xget_v(img_size,"depth"));

		
		full_annotation+="<size><width>%d</width><height>%d</height><depth>%d</depth></size>\n" % (img_w,img_h,img_d)

		scale=min(500/img_w,500/img_h);
		dX=(500-img_w*scale)/2;
		dY=(500-img_h*scale)/2;
		iSqn=1;
		for o in object_tags:

			object_name=xget_v(o,"name");
			bbox=xget_child(o,"bndbox");
			(o_xmin,o_xmax,o_ymin,o_ymax)=xget_v2(bbox,["xmin","xmax","ymin","ymax"])
			obj_xmin=float(o_xmin);
			obj_xmax=float(o_xmax);
			obj_ymin=float(o_ymin);
			obj_ymax=float(o_ymax);
			xmin=float(o_xmin)*scale+dX;
			xmax=float(o_xmax)*scale+dX;
			ymin=float(o_ymin)*scale+dY;
			ymax=float(o_ymax)*scale+dY;
			w=xmax-xmin;
			h=ymax-ymin;
			o_w=float(o_xmax)-float(o_xmin);
			o_h=float(o_ymax)-float(o_ymin);
			objS=min(500/o_w,500/o_h);
			dObjX=(500-o_w*objS)/2;
			dObjY=(500-o_h*objS)/2;

			object_xml="""
<bbox name="%s" sqn="1" left="%s" top="%s" width="%d" height="%d">
<pt x="%s" y="%s" ct="0"/>
<pt x="%s" y="%s" ct="0"/>
""" % (object_name, xmin,ymin,w,h,xmin,ymin,xmax,ymax)

			pose=xget_v_dft(o,"pose","Unspecified");
			truncated=xget_v_dft(o,"truncated","0");
			difficult=xget_v_dft(o,"difficult","0");
			occluded=xget_v_dft(o,"occluded","0");
			detail_xml=""

			detail_xml+="""
		<attribute name="truncated" value="%s" ct="0"/>
		<attribute name="occluded" value="%s" ct="0"/>
		<attribute name="difficult" value="%s" ct="0"/>
                <select name="pose" value="%s" ct="0"/>
""" % ( truncated,occluded,difficult,pose) 

			for part in xget(o,"part"):
				object_name=xget_v(part,"name");
				bbox=xget_child(part,"bndbox");
				(o_xmin,o_xmax,o_ymin,o_ymax)=xget_v2(bbox,["xmin","xmax","ymin","ymax"])
				p_xmin=float(o_xmin)*objS+dObjX-obj_xmin*objS;
				p_xmax=float(o_xmax)*objS+dObjX-obj_xmin*objS;
				p_ymin=float(o_ymin)*objS+dObjY-obj_ymin*objS;
				p_ymax=float(o_ymax)*objS+dObjY-obj_ymin*objS;
				p_w=p_xmax-p_xmin;
				p_h=p_ymax-p_ymin;
				part_xml="""
<bbox name="%s" sqn="1" left="%s" top="%s" width="%d" height="%d">
<pt x="%s" y="%s" ct="0"/>
<pt x="%s" y="%s" ct="0"/>
</bbox>
""" % (object_name, p_xmin,p_ymin,p_w,p_h,p_xmin,p_ymin,p_xmax,p_ymax)

				detail_xml+=part_xml

			iSqn = iSqn+1;
			object_xml+="<annotation>\n"+detail_xml+"</annotation>"
			object_xml+="</bbox>"
			full_annotation+=object_xml




		full_annotation+="</annotation></results>"
		annotation=Annotation(ref_data=dt_item,annotation_type=ann_type,author=request.user,data=full_annotation);
		annotation.save();
                TM.add_tag( annotation, tag_name)

			     
	resp.write("done");
	return resp







def add_child_boxes_for_annotation(request,a,ann_type_child):
    xmldoc = minidom.parseString(a.data);

    img_size=xget(xmldoc,"size")[0];

    img_w=float(xget_v(img_size,"width"));
    img_h=float(xget_v(img_size,"height"));
    
    scale=min(500/img_w,500/img_h);
    dX=(500-img_w*scale)/2;
    dY=(500-img_h*scale)/2;

    object_tags=xget(xmldoc,"bbox");
    for o in object_tags:
        (class_name,l,t,w,h)=xget_a2(o,["name","left","top","width","height"])
        l=(float(l)-dX)/scale
        t=(float(t)-dY)/scale
        w=float(w)/scale
        h=float(h)/scale
        box_data=u"%s\n%f,%f,%f,%f\n1.0\n" % (class_name,l,t,w,h)
        print box_data
        annotation=Annotation(ref_data=a.ref_data,annotation_type=ann_type_child,
                              author=request.user,data=box_data);
        annotation.save();
        annotation.rel_reference.add(a);
        annotation.save();

        tagging.models.Tag.objects.add_tag(annotation,"Source-Annotation")
        print tagging.models.Tag.objects.get_for_object(annotation)
        
                        

@login_required
def register_voc_box_child_annotations(request,dataset_name,annotation_id=None):
	if not request.user.has_perm('datastore.annotation.add'):
		return render_to_response('registration/not_authorized.html')

	annotation_type="voc2008_boxes"
	ann_type = get_object_or_404(AnnotationType,name=annotation_type);
	annotation_type_child="voc_bbox"
	ann_type_child = get_object_or_404(AnnotationType,name=annotation_type_child);

	dataset=get_object_or_404(Dataset,name=dataset_name);

	if annotation_id:	
		a=Annotation.objects.get(id=annotation_id);
		add_child_boxes_for_annotation(request,a,ann_type_child);
	else:
		for dt_item in dataset.dataitem_set.all():
			for a in dt_item.annotation_set.filter(is_active=True,annotation_type__id=ann_type.id):
				add_child_boxes_for_annotation(request,a,ann_type_child);

	resp=HttpResponse("done");
	return resp

@login_required
def register_labelme_box_child_annotations(request,dataset_name,annotation_id=None):
	if not request.user.has_perm('datastore.annotation.add'):
		return render_to_response('registration/not_authorized.html')

	annotation_type="LabelMe_boxes"
	ann_type = get_object_or_404(AnnotationType,name=annotation_type);
	annotation_type_child="voc_bbox"
	ann_type_child = get_object_or_404(AnnotationType,name=annotation_type_child);

	dataset=get_object_or_404(Dataset,name=dataset_name);

	if annotation_id:	
		a=Annotation.objects.get(id=annotation_id);
		add_child_boxes_for_annotation(request,a,ann_type_child);
	else:
		for dt_item in dataset.dataitem_set.all():
			for a in dt_item.annotation_set.filter(is_active=True,annotation_type__id=ann_type.id):
				add_child_boxes_for_annotation(request,a,ann_type_child);

	resp=HttpResponse("done");
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
	#for dt_item in dataset.dataitem_set.filter(id=29913): #url__contains="IMG_4093"):
	#totTODO=None
	totTODO=dataset.dataitem_set.all().count(); 
	for (iItem,dt_item) in enumerate(dataset.dataitem_set.all()): 
		
		(str_img,str_img_path,str_img_file)=dt_item.get_name_parts();    
		
		annotation_filename=os.path.join(annotation_path,str_img_path,str_img_file+".xml");
		if not os.path.exists(annotation_filename):
			resp.write("Missing annotations file for %s<br/>\n" % annotation_filename);
			continue

		x_out=minidom.Document();
		x_res = x_out.createElement("results")
		x_ann = x_out.createElement("annotation")

		xmldoc = minidom.parse(annotation_filename);
		object_tags=xget(xmldoc,"object");
		image_filename=os.path.join(dataset_path,str_img_path,str_img_file+".jpg");
		print iItem,totTODO,image_filename

		im = Image.open(image_filename);
		(img_w,img_h) = im.size;
		scale=min(500.0/img_w,500.0/img_h);
		dX=(500-img_w*scale)/2;
		dY=(500-img_h*scale)/2;
		iSqn=1;

		x_sz = x_out.createElement("size")
		xadd(x_out,x_sz,"width","%d" % img_w)
		xadd(x_out,x_sz,"height","%d" % img_h)
		x_ann.appendChild(x_sz);

		for o in object_tags:
			object_name = xget_v(o,"name")
			if not object_name:
				continue
			object_name = object_name.strip();
			#print o.toxml();
			polygon=xget(o,"polygon")[0];
			points=xget(polygon,"pt");
			points_new=[];
			for pt in points:
				x=float(xget_v(pt,"x"))
				y=float(xget_v(pt,"y"))
				points_new.append([x,y]);
			(o_xmin,o_ymin)=reduce(lambda (x,y),(x2,y2):(min(x,x2),min(y,y2)),points_new);
			(o_xmax,o_ymax)=reduce(lambda (x,y),(x2,y2):(max(x,x2),max(y,y2)),points_new);
			#print object_name, o_xmin,o_ymin, o_xmax,o_ymax,type(object_name)


			xmin=float(o_xmin)*scale+dX;
			xmax=float(o_xmax)*scale+dX;
			ymin=float(o_ymin)*scale+dY;
			ymax=float(o_ymax)*scale+dY;
			w=xmax-xmin;
			h=ymax-ymin;
			iSqn+=1;

			x_obj=x_out.createElement("bbox");
			x_obj.setAttribute(u"name",object_name)
			x_obj.setAttribute("left","%d" % xmin)
			x_obj.setAttribute("top","%d" % ymin)
			x_obj.setAttribute("width","%d" % w)
			x_obj.setAttribute("height","%d" % h)
			x_obj.setAttribute("sqn","1")

			x_pt=x_out.createElement("pt");
			x_pt.setAttribute("x","%d" % xmin)
			x_pt.setAttribute("y","%d" % ymin)
			x_pt.setAttribute("ct","0")
			x_obj.appendChild(pt)			

			x_pt=x_out.createElement("pt");
			x_pt.setAttribute("x","%d" % xmax)
			x_pt.setAttribute("y","%d" % ymax)
			x_pt.setAttribute("ct","0")
			x_obj.appendChild(pt)			

			x_ann.appendChild(x_obj);



		x_res.appendChild(x_ann);
		x_out.appendChild(x_res);
		#print minidom.parseString(force_unicode(x_out.toxml("utf-8")))
		#print x_out.toxml("utf-8")
		#print minidom.parseString(x_out.toxml("utf-8"))
		#print "-----"
		annotation=Annotation(ref_data=dt_item,annotation_type=ann_type,author=request.user,data=unicode(x_out.toxml("utf-8")))
		#print minidom.parseString(annotation.data);
		#print "====="

		annotation.save();
		#print minidom.parseString(annotation.data);
		a_id=annotation.id
		a_new=Annotation.objects.get(id=a_id)
		dt=a_new.data
		#print type(annotation.data)
		#print type(str(dt))
		#print str(dt)[1700:1800]
		#print annotation.data[1700:1800]
		#print minidom.parseString(str(dt)).toxml()
			     
	resp.write("Done importing LabelMe annotations as boxes");
	return resp




def score_predictions(request,dataset_name):

    annotation_type="voc_bbox"
    ann_type = get_object_or_404(AnnotationType,name=annotation_type);

    dataset_name="VOC2008";

    dataset=get_object_or_404(Dataset,name=dataset_name);

    annotations=TaggedItem.objects.get_by_model(Annotation,"Source-Annotation").filter(annotation_type__id=ann_type.id);


    pred_set=PredictionsSet.objects.get(id=1);
    predictions=[]
    for a in pred_set.annotations.all():
        (category,box,confidence)=a.data.split("\n")[0:3]
        predictions.append([a.ref_data.id,float(confidence),category,map(lambda s:float(s),box.split(","))]);

    predictions.sort(reverse=True)
  
    print predictions
    print pred_set.annotations.count();
    return HttpResponse("done");
    

def do_import_predictions(request,dataset_name,form,uploaded_file):
	
	annotation_type="voc_bbox"
	ann_type = get_object_or_404(AnnotationType,name=annotation_type);

	dataset=get_object_or_404(Dataset,name=dataset_name);

	pred_set=PredictionsSet(title=form.cleaned_data['title'],
				description=form.cleaned_data['description'],
				author=request.user);
	pred_set.save();

		
	for chunk in uploaded_file.chunks():
		for l in chunk.split("\n"):
			parts=l.strip().split(" ")
			object_name=form.cleaned_data['category']
			if len(parts)==6:
				(image_name,confidence,l,t,r,b)=parts
				di=dataset.dataitem_set.filter(url__contains=image_name)[0];
				w=float(r)-float(l);
				h=float(b)-float(t);
				box_data=u"%s\n%s,%s,%f,%f\n%s\n" % (object_name,l,t,w,h,confidence)
				print box_data
				annotation=Annotation(ref_data=di,annotation_type=ann_type,
						      author=request.user,data=box_data);
				annotation.save();
				pred_set.annotations.add(annotation);
				
@login_required
def register_voc_predictions(request,dataset_name):
	if not request.user.has_perm('datastore.annotation.add'):
		return render_to_response('registration/not_authorized.html')


	if request.method == 'POST':
		form = UploadPredictionsForm(request.POST, request.FILES)
		if form.is_valid():
			uploaded_file=request.FILES['predictions_file'];
			do_import_predictions(request,dataset_name,form,uploaded_file);
			#return HttpResponseRedirect('/datastore/')
	else:
		form = UploadPredictionsForm()
	return render_to_response('datastore/upload_predictions.html', {'form': form})



from forms import UploadPredictionsForm


def do_tag_images(request,dataset_name,form,uploaded_file):
	
	dataset=get_object_or_404(Dataset,name=dataset_name);

        TM=tagging.models.Tag.objects;
        tag_name=form.cleaned_data['tag_name'];

	for chunk in uploaded_file.chunks():
		for l in chunk.split("\n"):
			parts=l.strip().split(" ")
                        img=parts[0];
			print img
                        di=dataset.dataitem_set.filter(url__contains=img)[0]
                        TM.add_tag(di,tag_name);

				
@login_required
def tag_images(request,dataset_name):
	if not request.user.has_perm('datastore.annotation.add'):
		return render_to_response('registration/not_authorized.html')


	if request.method == 'POST':
		form = TagImagesForm(request.POST, request.FILES)
		if form.is_valid():
			uploaded_file=request.FILES['image_list_file'];
			do_tag_images(request,dataset_name,form,uploaded_file);
			#return HttpResponseRedirect('/datastore/')
	else:
		form = TagImagesForm()
	return render_to_response('datastore/tag_images.html', {'form': form})    





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

	results=ann_type.annotation_set.filter(ref_data__ds__id=ds.id).filter(is_active=True).order_by("ref_data__id");

	return object_list(request,queryset=results, paginate_by=20, page=page,
			template_name='datastore/annotation_list.html');


def show_random_annotations(request,dataset_name,annotation_type,num_samples=30):

	ds = get_object_or_404(Dataset,name=dataset_name)
	ann_type = get_object_or_404(AnnotationType,name=annotation_type)

	results=ann_type.annotation_set.filter(ref_data__ds__id=ds.id).filter(is_active=True).order_by("?");
	page=1
	return object_list(request,queryset=results, paginate_by=num_samples, page=page,
			template_name='datastore/annotation_list.html');




def show_flagged_annotations(request,dataset_name,flag_name,annotation_type=None,page=None):
	if not page:
		return redirect_to(request,"p1/");

	ds = get_object_or_404(Dataset,name=dataset_name)
	flag_ann_type = get_object_or_404(AnnotationType,name="flags")
	print annotation_type
	if annotation_type:
		ann_type = get_object_or_404(AnnotationType,name=annotation_type)
		results=Annotation.objects.filter(data=flag_name,annotation_type__id=flag_ann_type.id,ref_data__ds__id=ds.id,is_active=True) 
	else:
		results=Annotation.objects.filter(data=flag_name,ref_data__ds__id=ds.id,is_active=True) 
	return object_list(request,queryset=results, paginate_by=20, page=page,
			template_name='datastore/annotation_list2.html');


def show_bbox_objects(request,object_name,page=None,dataset_name=None):
	if not page:
		return redirect_to(request,"p1/");

	ann_type = get_object_or_404(AnnotationType,name="voc_bbox");

	results=Annotation.objects.filter(annotation_type__id=ann_type.id, data__contains=object_name);

	return object_list(request,queryset=results, paginate_by=20, page=page,
			template_name='datastore/annotation_list.html');

def show_item_annotation(request,item_name):
	di=DataItem.objects.filter(url__contains=item_name)[0];
	return show_data_item(request,di.id)

def show_data_item(request,item_id):
	di = get_object_or_404(DataItem,id=item_id);
	types=AnnotationType.objects.all();
	ann_types=map(lambda t:t.name,types);

	empty_ann_types={};
	for t in types:
		empty_ann_types[t.name]=t;
		
	types_dict={};
	for t in di.annotation_set.all():
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
        TM=tagging.models.Tag.objects;
        tag_name="Source-Annotation";
        
	if request.method=="POST":
		if "sites" in request.POST:
			val=request.POST["sites"]
			val="<?xml version='1.0'?>\n"+urllib.unquote(val);
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
		annotation=Annotation(ref_data=data_item,annotation_type=ann_type,author=request.user,data=val);
		annotation.save();
                TM.add_tag(annotation,tag_name);
		return redirect_to(request,"../../",permanent=False);
	else:
		return render_to_response('datastore/annotate_internal_'+ann_type.category+'.html',
					  {'object':data_item,'ann_type':ann_type });

@login_required
def new_visual_similarity(request,ann1_id,ann2_id):
	if not request.user.has_perm('datastore.annotation.add'):
		return render_to_response('registration/not_authorized.html')

	annotation_type="visual_similarity";
	ann_type = get_object_or_404(AnnotationType,name=annotation_type);

	ann1 = get_object_or_404(Annotation,id=ann1_id);
	ann2 = get_object_or_404(Annotation,id=ann2_id);

	if request.method=="POST":
		attributes = ann_type.get_annotation_metadata2()['attributes']
		x_doc=minidom.Document();
		x_res = x_doc.createElement("similarity")
		x_doc.appendChild(x_res);
		x_ref = x_doc.createElement("compare")
		x_res.appendChild(x_ref);
		xadd(x_doc,x_ref,"a","%d" % ann1.id)	
		xadd(x_doc,x_ref,"b","%d" % ann2.id)
		for a in attributes:
			fn=a.replace(" ","-");
			if fn in request.POST:
                            sim_ann=request.POST[fn]
                        else:
                            sim_ann="-1"
			sim_exp=request.POST[fn+"_explanation"]
			print sim_ann
			print sim_exp
			x_sim = x_doc.createElement("similarity")
			x_res.appendChild(x_sim);
			xadd(x_doc,x_sim,"attribute",a)
			xadd(x_doc,x_sim,"value",sim_ann)
			xadd(x_doc,x_sim,"explanation",sim_exp)
		#val = x_doc.toxml()
		val = unicode(x_doc.toxml("utf-8"))
		print val
		
		annotation=Annotation(ref_data=ann1.ref_data,annotation_type=ann_type,author=request.user,data=val);
		annotation.save();
		annotation.rel_reference.add(ann1);
		annotation.rel_reference.add(ann2);
		annotation.save();

		return redirect_to(request,"../../../",permanent=False);
		#return render_to_response('datastore/annotate_internal_'+ann_type.category+'.html',
		#			  {'ann1':ann1,'ann2':ann2,'ann_type':ann_type });
	else:
		return render_to_response('datastore/annotate_internal_'+ann_type.category+'.html',
					  {'ann1':ann1,'ann2':ann2,'ann_type':ann_type });


@login_required
def random_similarity_task(request,dataset_name,query):
	if not request.user.has_perm('datastore.annotation.add'):
		return render_to_response('registration/not_authorized.html')

	ds = get_object_or_404(Dataset,name=dataset_name);
	ann_type=get_object_or_404(AnnotationType,name="visual_similarity");
	base_ann_type=get_object_or_404(AnnotationType,name="voc_bbox");
	available_objects=Annotation.objects.filter(ref_data__ds__id=ds.id,annotation_type__id=base_ann_type.id,data__contains=query)
	num_objects=available_objects.count();
	print num_objects
	idx_a=random.randint(0,num_objects-1)
	idx_b=random.randint(0,num_objects-1)
	print idx_a,idx_b	
	ann_a= available_objects[idx_a];
	ann_b= available_objects[idx_b];
	return redirect_to(request,"new_visual_similarity/%d/%d/" %(ann_a.id,ann_b.id),permanent=False);




@login_required
def edit_annotation_inline(request,annotation_id):
	if not request.user.has_perm('datastore.annotation.add'):
		return render_to_response('registration/not_authorized.html')

	base_annotation = get_object_or_404(Annotation,id=annotation_id);
	ann_type = base_annotation.annotation_type;

	if request.method=="POST":
		if "sites" in request.POST:
			val=request.POST["sites"]
			val="<?xml version='1.0'?>\n"+urllib.unquote(val);
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
		annotation=Annotation(ref_data=base_annotation.ref_data,annotation_type=ann_type,author=request.user,data=val);
		annotation.id=base_annotation.id;
		annotation.created=datetime.datetime.today();
		annotation.is_active=True;
		annotation.save();
		base_annotation.id=None;
		base_annotation.is_active=False;
		base_annotation.save();
		rev=AnnotationRevisions(target_annotation=annotation,revision=base_annotation,author=request.user);
		rev.save();
		return redirect_to(request,"../../../",permanent=False);
	else:
		return render_to_response('datastore/edit_internal_'+ann_type.category+'.html',
					  {'current_annotation':base_annotation });

@login_required
def flag_annotation(request,annotation_id,flag):
	ann_type = get_object_or_404(AnnotationType,name="flags");
	ref_annotation = get_object_or_404(Annotation,id=annotation_id);

	if not request.user.has_perm('datastore.annotation.add'):
		return render_to_response('datastore/flag.html',{'state':'off','flag':flag,'ref':ref_annotation})

	annotation=Annotation(ref_data=ref_annotation.ref_data,annotation_type=ann_type,author=request.user,data=flag);
	annotation.save();
	annotation.rel_reference.add(ref_annotation);
	annotation.save();
	return render_to_response('datastore/flag.html',{'state':'on','flag':flag,'annotation':annotation,'ref':ref_annotation})


@login_required
def unflag_annotation(request,annotation_id,flag):
	ann_type = get_object_or_404(AnnotationType,name="flags");
	ref_annotation = get_object_or_404(Annotation,id=annotation_id);

	if not request.user.has_perm('datastore.annotation.delete'):
		no_general_auth=True
	else:
		no_general_auth=False

	has_active=False;
	for a in Annotation.objects.filter(annotation_type__id=ann_type.id, data=flag, rel_reference__id=ref_annotation.id,is_active=True).all():
		if no_general_auth:
			if not a.author.id==request.user.id:
				has_active=True
				continue
		a.is_active=False;
		a.save();

	if has_active:
		return render_to_response('datastore/flag.html',{'state':'on','flag':flag,'ref':ref_annotation})
	else:
		return render_to_response('datastore/flag.html',{'state':'off','flag':flag,'ref':ref_annotation})


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

def index(request):
	datasets=Dataset.objects.all()
	return render_to_response('datastore/index.html',
		  {'datasets':datasets});
