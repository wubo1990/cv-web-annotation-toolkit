#! /usr/bin/python
#***********************************************************
#* Software License Agreement (BSD License)
#*
#*  Copyright (c) 2008, Alexander Sorokin
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
#Author: Alexander Sorokin

"""
Generate bounding box quality evaluation dataset

usage: %(progname)s --submissions=<submission_datasets> --gold_standard=<gold_standard_dataset> --saveto=<save_problem> 

  
"""

import uuid,sys,os, string, time, getopt
import roslib; roslib.load_manifest('crowd_quality')
import rospy

import os, sys, getopt

from cv_mech_turk2.session_results import SessionResults
from cv_mech_turk2.tasks.boxes import *

from copy import copy

import cvxmod 

from mech_turk.io_helper import *


import yaml

import numpy,random

from crowd_quality.features import *
from generate_bbox_dataset import *


def gt_valid_counts(gold_standard_session,gold_standard_annotation,name_map=None):
  gold_boxes=gold_standard_session.get_bounding_boxes(gold_standard_annotation);
  
  if name_map:
    filter_boxes_in_place(gold_boxes,name_map)

  return len(gold_boxes)


def compute_gt_counts(all_examples,gold_standard,name_map=None):
  all_gt_counts={}
  for ex in all_examples:
    if ex.work_unit in gold_standard.annotations:
      c=gt_valid_counts(gold_standard,gold_standard.annotations[ex.work_unit][0],name_map);
      all_gt_counts[ex.id]=c
    else:
      print " No GT for ",ex.work_unit.id
  return all_gt_counts



def extract_all_features(all_examples,name_map=None):
  all_features=[];

  for example in all_examples:
    example_boxes = example.session.get_bounding_boxes(example.target_submission);
    if name_map:
      filter_boxes_in_place(example_boxes,name_map)
      
    num_boxes=len(example_boxes);
    worker_id=example.session.get_worker_id(example.target_submission);

    features=[worker_id,example.work_unit,str(num_boxes)];

    all_features.append(features)
    
  feature_schema=[ FeatureDescription('WorkerID',FeatureDescription.NOMINAL),
                   FeatureDescription('ObjectID',FeatureDescription.NOMINAL),
                   FeatureDescription('Box_count',  FeatureDescription.NOMINAL)]

  return (all_features,feature_schema)


        

def PI_save_dataset(saveto_dir,prefix,set_name,all_features,feature_schema,all_examples,gt_quality=None):
  ensure_dir(saveto_dir)

  with open(os.path.join(saveto_dir,prefix+"."+set_name),'w') as f_all_examples:
    for ex,fs in zip(all_examples,all_features):

      for i,(f,desc) in enumerate(zip(fs,feature_schema)):
        if i==0:
          f_all_examples.write(desc.format(f))
        else:
          f_all_examples.write(","+desc.format(f))

      print >>f_all_examples

  with open(os.path.join(saveto_dir,prefix+"."+set_name+".id"),'w') as f_example_ids:
    for ex in all_examples:
      print >>f_example_ids, ex.id, ex.session.location, ex.work_unit, ex.target_submission

  if gt_quality:
    with open(os.path.join(saveto_dir,prefix+"."+set_name+'.gt.txt'),'w') as f_gt_quality:
      for ex in all_examples:
        gt=gt_quality[ex.id];
        print >>f_gt_quality,gt

    with open(os.path.join(saveto_dir,prefix+"."+set_name+'.gt_full.txt'),'w') as f_gt_quality:
      for ex in all_examples:
        gt=gt_quality[ex.id];
        print >>f_gt_quality,gt,ex.id,ex.work_unit



def save_dataset(saveto_dir,all_features,feature_schema,all_examples,gt_quality):
  prefix="data"
  random.seed(1234);

  datasets=split_dataset([0.5,0.25,0.25],all_features,all_examples)

  for ds,set_name in zip(datasets,['train','valid','test']):
    PI_save_dataset(saveto_dir,prefix,set_name,ds[0],feature_schema,ds[1],gt_quality)



def usage(progname):
  print __doc__ % vars()

def main(argv, stdout, environ):
  progname = argv[0]
  optlist, args = getopt.getopt(argv[1:], "", ["help", "submissions=", "gold_standard=", "saveto=","names="]);

  submission_datasets=None
  gold_standard=None
  saveto_dir=None
  names=None

  for (field, val) in optlist:
    if field == "--help":
      usage(progname)
      return
    elif field == "--submissions":
        submission_datasets=val.split(',');
    elif field == "--gold_standard":
        gold_standard=val;
    elif field == "--saveto":
        saveto_dir=val;
    elif field == "--names":
        names=val;

  if submission_datasets is None or saveto_dir is None:
    usage(progname);
    return

  if names:
    name_map=load_name_map(names)
  else:
    name_map=None


  submission_sessions=[];
  for ds in submission_datasets:
    results=SessionResults();
    results.read_results(ds)
    submission_sessions.append(results);

  if gold_standard:
    gold_standard_session=SessionResults()
    gold_standard_session.read_results(gold_standard)
  else:
    gold_standard_session=None

  
  all_submissions={};
  for s in submission_sessions:
    collect_submissions(s,all_submissions);

  all_examples=[];
  all_examples.extend(create_examples(all_submissions));

  if gold_standard_session:
    gt_values=compute_gt_counts(all_examples,gold_standard_session,name_map)
  else:
    gt_values=None

  (all_features,feature_schema)=extract_all_features(all_examples,name_map)

  save_dataset(saveto_dir,all_features,feature_schema,all_examples,gt_values)
    


    

if __name__ == "__main__":
  main(sys.argv, sys.stdout, os.environ)
