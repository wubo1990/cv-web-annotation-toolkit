
from django import template
from django.utils.safestring import mark_safe

import time, datetime

register = template.Library()


def calc_delay(d1, d2):
  if d1 and d2:
    return d1-d2
  return "delay"

@register.filter
def AP(ap):
  if ap==0:
    return "-"

  s = "%0.1f" % (ap*100);
  return s;


@register.filter
def ACCURACY(ap):
  if ap==0:
    return "-"

  s = "%0.1f" % (ap);
  return s;

@register.filter
def NWINS(n):
  if n==0:
    return ""
  return "%d" % n
