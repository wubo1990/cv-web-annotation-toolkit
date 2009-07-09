# Create your views here.

import urllib,uuid,os,sys,shutil,subprocess
import cPickle as pickler

from django.conf import settings

from django.http import HttpResponse,Http404,HttpResponseRedirect
from django.shortcuts import render_to_response,get_object_or_404 
from django.views.generic.list_detail import object_list

try:
  from boto.mturk.connection import MTurkConnection
  from boto.mturk.question import ExternalQuestion
  from boto.mturk.qualification import Qualifications, PercentAssignmentsApprovedRequirement
  hasBoto=True
except Exception,e:
  print e
  hasBoto=False
    
from models import *

from django.contrib import admin

from django.contrib.admin.views import main

def add_session(request):
  res = main.add_stage(request, "mturk", "session")
  if request.POST:
    pass
  else:
    pass
  return res

def edit_session(request, object_id):
  session = get_object_or_404(Session, pk=object_id)
  if not session.owner:
    session.owner = request.user
    session.save()

  if request.POST:
    if not request.user.is_superuser:
      if request.user != session.owner:
        return HttpResponseRedirect('/admin/?next=%s' % request.path)

  ret = main.change_stage(request, "mturk", "session", object_id)

  session = get_object_or_404(Session, pk=object_id)

  if session.owner is None:
    session.owner = request.user
    session.save()
  return ret

def delete_session(request, object_id):
  session = get_object_or_404(Session, pk=object_id)
  if not request.user.is_superuser:
    if request.user != session.owner:
      return HttpResponseRedirect('/admin/?next=%s' % request.path)
  return main.delete_stage(request, "mturk", "session", object_id)

def edit_task(request, object_id):
  task = get_object_or_404(Task, pk=object_id)
  return main.change_stage(request, "mturk", "task", object_id)

def delete_task(request, object_id):
  task = get_object_or_404(Task, pk=object_id)
  return main.delete_stage(request, "mturk", "task", object_id)
  


