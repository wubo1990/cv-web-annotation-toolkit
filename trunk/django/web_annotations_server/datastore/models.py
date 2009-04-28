from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Dataset(models.Model):
    name=models.SlugField();

    def __init__(self,*args):
	models.Model.__init__(self,*args)

    def __str__(self):
        return self.name


    def get_stat_counts(self):
	if "stat_counts" in self.__dict__:
		return self.stat_counts
	else:
		voc2008_box_AT=AnnotationType.objects.get(name="voc2008_boxes");
		voc_bbox_AT=AnnotationType.objects.get(name="voc_bbox");
		LabelMe_boxes_AT=AnnotationType.objects.get(name="LabelMe_boxes");

		flag_AT=AnnotationType.objects.get(name="flags");
		flag_AT
		num_flags={};
		for flag_name in ["red","white","blue"]:
			c=DataItem.objects.filter(annotation__annotation_type__id=flag_AT.id,ds__id=self.id,annotation__data=flag_name,annotation__is_active=True).count()
			num_flags[flag_name]=c;
		self.stat_counts={
			'data_items':self.dataitem_set.count(),
			'voc2008_boxes':DataItem.objects.filter(annotation__annotation_type__id=voc2008_box_AT.id,ds__id=self.id).count(),
			'LabelMe_boxes':DataItem.objects.filter(annotation__annotation_type__id=LabelMe_boxes_AT.id,ds__id=self.id).count(),
			'voc_bbox':DataItem.objects.filter(annotation__annotation_type__id=voc_bbox_AT.id,ds__id=self.id).count(),
			'num_flags':num_flags
		};
		return self.stat_counts


class DataItem(models.Model):
    url=models.TextField();
    type=models.SlugField();
    ds=models.ForeignKey(Dataset); 

    def __str__(self):
        return "%s(%d,%s)" % (self.ds.name,self.id,self.url)

    def get_public_id(self):
	return self.url

    def get_name_parts(self):
        str_img=self.url.split("/")
        str_img_file=str_img[-1].split(".")[0];
        path_components=str_img[3:len(str_img)-1];
        if path_components:
            str_img_path=reduce(lambda a,b:a+"/"+b,path_components);
            str_img=str_img_path+"/"+str_img_file
        else:
            str_img_path="";
            str_img=str_img_file;

        return (str_img,str_img_path,str_img_file);

class AnnotationType(models.Model):
    category=models.SlugField();
    name=models.SlugField();

    annotation_metadata=models.TextField(blank=True);
    explanation=models.URLField(blank=True);

    def __str__(self):
        return self.name

    def get_annotation_metadata(self):
        metadata=self.annotation_metadata.split("&");
        meta_dict={}
        for (k,v) in map(lambda v:v.split("="),metadata):
            meta_dict[k]=v;
        return meta_dict;


class Annotation(models.Model):
    ref_data=models.ForeignKey(DataItem);
    annotation_type=models.ForeignKey(AnnotationType);
    author=models.ForeignKey(User);
    created = models.DateTimeField(auto_now_add=True);

    is_active=models.BooleanField(default=True);
    is_locked=models.BooleanField(default=False);

    data=models.TextField();
    canonic_url=models.URLField(blank=True);


    rel_reference = models.ManyToManyField('self', symmetrical=False,blank=True)




	
