
import time, datetime
from django import template
register = template.Library()

from django.utils.safestring import mark_safe



@register.filter
def render_annotation_mini(a):
  if a.annotation_type.category=="keywords":
    return a.data;
  if a.annotation_type.category=="text":
    return a.data;
  if a.annotation_type.category=="gxml":
    str_img=a.ref_data.url.split("/")[-1];
    str_img=str_img.split(".")[0];
    
    metadata=a.annotation_type.annotation_metadata.split("&");
    task=""
    for (k,v) in map(lambda v:v.split("="),metadata):
      if k=="task":
        task=v;

    str_gxml="<iframe id='show_ann_%d' width='350' height='350' src='/code/gxml_show.html?swf=label_generic&swf_w=300&swf_h=300&img_base=%s&video=%s&frame=%s&task=%s&mode=display&annotationURL=/datastore/annotation/%d/'></iframe>" % (a.id,"/",a.ref_data.ds.name,str_img,task,a.id)
    return mark_safe(str_gxml)

  return "%s" % a.annotation_type.category

render_annotation_mini.is_safe=True;





