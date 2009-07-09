
import time, datetime
from django import template
from datastore.models import Annotation,AnnotationType
from django.template.loader import render_to_string

register = template.Library()

from django.utils.safestring import mark_safe


@register.simple_tag
def std_navigator(paginator,page,template_plain='paginator/plain.html',template_compact='paginator/compact.html'):
  if paginator.num_pages<10:
    return render_to_string(template_plain, { 'paginator': paginator })

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

