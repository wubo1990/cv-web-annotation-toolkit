from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Dataset(models.Model):
    name=models.SlugField();
    def __str__(self):
        return self.name

class DataItem(models.Model):
    url=models.TextField();
    type=models.SlugField();
    ds=models.ForeignKey(Dataset); 

    def __str__(self):
        return "%s(%d,%s)" % (self.ds.name,self.id,self.url)


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

    is_active=models.BooleanField(default=True);

    data=models.TextField();
    canonic_url=models.URLField(blank=True);


    rel_reference = models.ManyToManyField('self', symmetrical=False,blank=True)




	
