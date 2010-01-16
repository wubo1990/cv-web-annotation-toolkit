#! /usr/bin/python

#***********************************************************
#* Software License Agreement (BSD License)
#*
#*  Copyright (c) 2008, Willow Garage, Inc.
#*  All rights reserved.
#*
#*  Redistribution and use in source and binary forms, with or without
#*  modification, are permitted provided that the following conditions
#*  are met:
#*
#*   * Redistributions of source code must retain the above copyright
#*     notice, this list of conditions and the following disclaimer.
#*   * Redistributions in binary form must reproduce the above
#*     copyright notice, this list of conditions and the following
#*     disclaimer in the documentation and/or other materials provided
#*     with the distribution.
#*   * Neither the name of the Willow Garage nor the names of its
#*     contributors may be used to endorse or promote products derived
#*     from this software without specific prior written permission.
#*
#*  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#*  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#*  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
#*  FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
#*  COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
#*  INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
#*  BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#*  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#*  CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
#*  LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
#*  ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
#*  POSSIBILITY OF SUCH DAMAGE.
#***********************************************************

"""
Compute submission agreement matrix:
usage: %(progname)s --annotations=<data_annotations_dir> --saveto=<save_problem_structure> --task=<task type>

  * task=<task type> - task type can be :
  *       "group" or 
  *       "bbox"[future] or 
  *       "outline"[future] or
  *       "attribute-rank".
  
"""

import uuid,sys,os, string, time, getopt
import roslib; roslib.load_manifest('crowd_quality')
import rospy

import os, sys, getopt

from mech_turk.tasks import group_images





def compute_task_agreements(all_submissions,saveto_dir,agreement_function):
  print "Processing %d submissions" % len(all_submissions)

  item_2_id={};
  item_2_submission={}
  for s in all_submissions:
    for k in s.keys():
      if k in item_2_submission:
        item_2_submission[k].append(s);
      else:
        item_2_submission[k]=[s];

      if k not in item_2_id:
        item_2_id[k]=len(item_2_id.keys())
  
  


  submission_agreements=[]

  for iSubmission,s in enumerate(all_submissions):
    relevant_submissions={};
    for item in s.keys():
      for subm in item_2_submission[item]:
        if subm.id==s.id:
          continue

        if subm in relevant_submissions:
          relevant_submissions[subm] += 1;
        else:
          relevant_submissions[subm] = 1;

    for (item,counts) in relevant_submissions.items():
      if counts>1:
        submission_agreements.append((s,item,agreement_function(s,item)))

  agreement_fn=os.path.join(saveto_dir,'agreement.txt')
  fAgreement=open(agreement_fn,'w');
  for sA,sB,agreement in submission_agreements:
    print >>fAgreement, sA.id,sB.id,agreement
  fAgreement.close()

  submission_ids_fn=os.path.join(saveto_dir,'submission_ids.txt')
  fSubmissionId=open(submission_ids_fn,'w')
  for s in all_submissions:
    print >>fSubmissionId, s.id,s.submission_id
  fSubmissionId.close();

def usage(progname):
  print __doc__ % vars()

def main(argv, stdout, environ):
  progname = argv[0]
  optlist, args = getopt.getopt(argv[1:], "", ["help", "annotations=","saveto=","task="])
  annotations_dir=None
  saveto_dir=None
  task_type="group"

  for (field, val) in optlist:
    if field == "--help":
      usage(progname)
      return
    elif field == "--annotations":
        annotations_dir=val;
    elif field == "--saveto":
        saveto_dir=val;
    elif field == "--task":
        task_type=val;

  if annotations_dir is None or saveto_dir is None:
    usage(progname);
    return

  if task_type=="group":
    all_submissions = group_images.read_submissions(annotations_dir,True)
    submission_2_id=group_images.assign_sequential_ids(all_submissions)
    agreement_function=group_images.compute_agreement;

  compute_task_agreements(all_submissions,saveto_dir,agreement_function)

    

if __name__ == "__main__":
  main(sys.argv, sys.stdout, os.environ)
