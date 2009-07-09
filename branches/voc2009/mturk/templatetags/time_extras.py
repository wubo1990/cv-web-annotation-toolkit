
from django import template

import time, datetime

register = template.Library()


def calc_delay(d1, d2):
  if d1 and d2:
    return d1-d2
  return "delay"

def human_date(d1):
  if not d1: return "None"

  today = datetime.datetime.today()
  s =  ""
  if today.year != d1.year:
    s = d1.strftime("%y-%m-%d %H:%M:%S")
  elif today.month != d1.month:
    s = d1.strftime("%b-%d %H:%M:%S")
  elif today.day != d1.day:
    s = d1.strftime("%b-%d %H:%M:%S")
  else:
    if d1.minute == 0:
      s = d1.strftime("%I %P")
    else:
      s = d1.strftime("%I:%M %P")
    if s[0] == '0': s=s[1:]
  return s

def relative_using_date(date):
  if not date: return "None"

  today = datetime.datetime.today()
  dt = today - date

  s = ""
  hours = dt.seconds / 3600
  minutes = dt.seconds / 60

  if abs(today.day-date.day) > 1:
    if dt.days == 1:
      s = "(%d day ago)" % dt.days
    elif dt.days < 30:
      s = "(%d days ago)" % dt.days
    elif dt.months < 12:
      s = "(%d months ago)" % dt.months
  else:
    hours = hours + dt.days * 24
    if hours > 1:
      s = "(%d hours ago)" % hours
    elif hours == 1:
      s = "(%d hour ago)" % hours
    elif hours < 1:
      s = "(%d minutes ago)" % minutes
  return s
      
      
      

from django import template
register = template.Library()
register.filter('calc_delay', calc_delay)
register.filter('human_date', human_date)
register.filter('relative_using_date', relative_using_date)
