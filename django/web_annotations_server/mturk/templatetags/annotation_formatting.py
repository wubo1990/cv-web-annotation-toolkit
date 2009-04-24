
import time, datetime
from django import template
register = template.Library()

from django.utils.safestring import mark_safe


@register.filter
def render_annotation_full(a):
  return render_annotation_mini(a,500,500)

@register.filter
def render_annotation_mini(a,w=None,h=None):
  """
  print dir(a.rel_reference)
  print dir(a)
  print a.rel_reference.reverse()
  print a.rel_reference.select_related()
  print a.rel_reference.target_col_name
  print a.rel_reference.source_col_name
  print a.annotation_set.count()
  """
  if a.annotation_set.count()>0:
    has_ref_str="(+)";
  else:
    has_ref_str="";

  if a.annotation_type.category=="keywords":
    return a.data+has_ref_str;
  if a.annotation_type.category=="text":
    return a.data+has_ref_str;
  if a.annotation_type.category=="gxml":
    (str_img,str_img_path,str_img_file)=a.ref_data.get_name_parts();    
    
    metadata=a.annotation_type.annotation_metadata.split("&");
    task=""
    for (k,v) in map(lambda v:v.split("="),metadata):
      if k=="task":
        task=v;

    if not w:
      w=350;
    if not h:
      h=350;

    str_gxml="<iframe id='show_ann_%d' width='%d' height='%d' marginheight='0' marginwidth='0' src='/code/gxml_show.html?swf=label_generic&swf_w=%d&swf_h=%d&img_base=%s&video=%s&frame=%s&task=%s&mode=display&annotationURL=/datastore/annotation/%d/'></iframe>" % (a.id,w,h,w,h,"/",a.ref_data.ds.name,str_img,task,a.id)
    return mark_safe(str_gxml+has_ref_str)
  if a.annotation_type.category=="grade10":
    h={}
    for p in map(lambda v:v.split("="),a.data.split('&')):
      k=p[0];
      if len(p)>1:
        v=p[1];
      else:
        v=""
      h[k]=v
      print h
    if h['av_feedback']:
      fback='('+h['av_feedback']+')'
    else:
      fback='';
    return h['av_quality']+fback+has_ref_str;

  return "%s" % a.annotation_type.category

render_annotation_mini.is_safe=True;





