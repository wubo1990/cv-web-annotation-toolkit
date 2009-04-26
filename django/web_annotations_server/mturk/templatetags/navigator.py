
import time, datetime
from django import template
from datastore.models import Annotation,AnnotationType
from django.template.loader import render_to_string

register = template.Library()

from django.utils.safestring import mark_safe

@register.filter
def render_annotation_large(a):
  return render_annotation_mini(a,800,800)

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
render_annotation_large.is_safe=True;
render_annotation_full.is_safe=True;

@register.filter
def do_flags(a):
  #str=" ";
  #for flag in ["white","blue","red"]:
  #  str+="<a href='/datastore/annotation/%d/flag/%s/' target='_rcd_flag'><img src='/code/images/ico/flag_%s.gif'><a/>" % (a.id,flag,flag)
  #str+=" ";
  flags_id=AnnotationType.objects.get(name="flags").id;
  str="\n<table><tr><script>\n";
  for flag in ["white","blue","red"]:
    if Annotation.objects.filter(annotation_type__id=flags_id, data=flag, rel_reference__id=a.id,is_active=True).count()>0:
      flag_val=1;
    else:
      flag_val=0;
    str+="\tcreate_flag(%d,'%s',%d);\n" % (a.id,flag,flag_val)
  str+="</script></tr></table>\n";
  return mark_safe(str);


@register.simple_tag
def std_navigator(paginator,page,template_plain='paginator/plain.html',template_compact='paginator/compact.html'):
  print dir(paginator)
  print dir(page)
  if paginator.num_pages<10:
    return render_to_string(template_plain, { 'paginator': paginator })
  print dir(paginator)
  pages=[];
  iP=page;
  s=-1;
  iP=iP+s;
  while iP >1:
    pages.append(iP);
    iP=iP+s;
    s*=2;
  pages.append(1);
  pages.reverse();
  pages_before=pages;
  pages=[];
  iP=page;
  s=1;
  iP=iP+s;
  while iP < paginator.num_pages:
    pages.append(iP);
    iP=iP+s;
    s*=2;
  pages.append(paginator.num_pages);
  pages_after=pages;


  return render_to_string(template_compact, { 'paginator': paginator,'pages_before':pages_before,'pages_after':pages_after,'page':page })

