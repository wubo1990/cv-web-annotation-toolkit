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

from __future__ import with_statement

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


class BboxAgreementExample:
  def __init__(self,global_id,relative_id,work_unit,target_submission,session,other_submissions):
    if global_id is not None:
      self.id=global_id
    else:
      self.id=uuid.uuid4();

    self.relative_id=relative_id

    self.session=session
    self.work_unit=work_unit
    self.target_submission=target_submission
    self.other_submissions=other_submissions







def collect_submissions(session,all_submissions):
  session_examples=[];
  for work_unit in session.images:
    if work_unit not in all_submissions:
      submission_list=[];
      all_submissions[work_unit]=submission_list;
    else:
      submission_list=all_submissions[work_unit]

    for iS,submission in enumerate(session.annotations[work_unit]):
      submission_list.append((work_unit,submission,session))


def create_examples(all_submissions):
  session_examples=[];

  for work_unit,work_unit_submissions in all_submissions.items():
    for iS,(work_unit,submission,session) in enumerate(work_unit_submissions):
      other_submissions=copy(work_unit_submissions)
      del other_submissions[iS];

      example=BboxAgreementExample(None,(work_unit,iS),work_unit,submission,session,other_submissions);
      session_examples.append(example);
    
  return session_examples


def compute_agreement(example,gold_standard_session,gold_standard_annotation,name_map=None):
  example_boxes = example.session.get_bounding_boxes(example.target_submission);
  gold_boxes=gold_standard_session.get_bounding_boxes(gold_standard_annotation);
  
  if name_map:
    filter_boxes_in_place(example_boxes,name_map)
    filter_boxes_in_place(gold_boxes,name_map)


  return compute_bbox_set_agreement(example_boxes,gold_boxes)



def compute_bbox_set_agreement(example_boxes,gold_boxes):
  nExB=len(example_boxes)
  nGtB=len(gold_boxes)  
  if nExB==0:
    if nGtB==0:
      return 1;
    else:
      return 0;

  if nGtB==0:
    print "WARNING: new object"
    return 0;

  A=cvxmod.zeros(rows=nExB, cols=nGtB)
  
  for iBox,ex in enumerate(example_boxes):
    for jBox,gt in enumerate(gold_boxes):
      A[iBox,jBox]=ex.overlap_score(gt);

  S=[];
  S2=[];

  for iBox,ex in enumerate(example_boxes):
    S_tmp=[0]*(iBox)*nGtB + [1]*nGtB + [0]*(nExB-iBox-1)*nGtB;

    S.append(S_tmp);

  for jBox in range(0,nGtB):
    S2_tmp=[0]*nExB*nGtB;
    for j2 in range(0,nExB):
      S2_tmp[j2*nGtB+jBox]=1;

    S2.append(S2_tmp);

  S=cvxmod.transpose(cvxmod.matrix(S,size=(nExB*nGtB,nExB)));
  S2=cvxmod.transpose(cvxmod.matrix(S2,size=(nExB*nGtB,nGtB)));

  A2=cvxmod.matrix(A,(1,nExB*nGtB));
  x = cvxmod.optvar('x', rows=nExB*nGtB,cols=1);

  p=cvxmod.problem(cvxmod.maximize(A2*x));  
  p.constr.append(x<=1)
  p.constr.append(x>=0)

  p.constr.append(S*x<=1)
  p.constr.append(S2*x<=1)

  p.solve(True)
  overlap=cvxmod.value(p)/max(nExB,nGtB);
  assert(overlap<1.0001);
  return overlap

  
def compute_gt_quality(all_examples,gold_standard,name_map=None,agreement_function=compute_agreement):
  all_quality={}
  for ex in all_examples:
    if ex.work_unit in gold_standard.annotations:
      quality=agreement_function(ex,gold_standard,gold_standard.annotations[ex.work_unit][0],name_map);
      all_quality[ex.id]=quality
    else:
      print " No GT for ",ex.work_unit.id
  return all_quality




def extract_all_features(all_examples,name_map=None):
  all_features=[];

  for example in all_examples:
    example_boxes = example.session.get_bounding_boxes(example.target_submission);
    if name_map:
      filter_boxes_in_place(example_boxes,name_map)
      


    agreement_with_others=[]
    other_length=[]
    if len(example.other_submissions)==0:
      agreement_with_others=[0]
      other_length=[0]

    for o_wu,o_subm,o_session in example.other_submissions:
      
      other_boxes = o_session.get_bounding_boxes(o_subm);
      filter_boxes_in_place(other_boxes,name_map)

      agreement=compute_bbox_set_agreement(example_boxes,other_boxes)
      agreement_with_others.append(agreement)

      other_length.append(len(other_boxes));

    features=[max(agreement_with_others), numpy.median(agreement_with_others), len(example_boxes), max(other_length), numpy.median(other_length),len(example.other_submissions)]

    all_features.append(features)
    
  feature_schema=[ FeatureDescription('Max_agreement',FeatureDescription.CONTINUOUS),
                   FeatureDescription('Median_agreement',FeatureDescription.CONTINUOUS),
                   FeatureDescription('Num_boxes',FeatureDescription.CONTINUOUS),
                   FeatureDescription('Max_other_num_boxes',FeatureDescription.CONTINUOUS),
                   FeatureDescription('Media_other_num_boxes',FeatureDescription.CONTINUOUS),
                   FeatureDescription('Num_other_submissions',FeatureDescription.CONTINUOUS)];

  return (all_features,feature_schema)


def AG_write_attr_file(saveto_dir,prefix,feature_schema):
    with open(os.path.join(saveto_dir,prefix+".attr"),'w') as f_schema:
      print >>f_schema, "target: cont (class)."
      for fd in feature_schema:
        print >>f_schema, "%s: %s." %(fd.name,fd.feature_type)
        

def AG_save_dataset(saveto_dir,prefix,set_name,all_features,feature_schema,all_examples,gt_quality=None):
  ensure_dir(saveto_dir)

  with open(os.path.join(saveto_dir,prefix+"."+set_name),'w') as f_all_examples:
    for ex,fs in zip(all_examples,all_features):
      if gt_quality is not None:
        print >>f_all_examples, gt_quality[ex.id],
      else:
        print >>f_all_examples, 0,

      for f,desc in zip(fs,feature_schema):
        print >>f_all_examples, desc.format(f),

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



def my_unzip2(train_set):
  return ([ f for f,ex in train_set],[ ex for f,ex in train_set])

def split_dataset(split_ratios,all_features,all_examples):
   examples=zip(all_features,all_examples)
   random.shuffle(examples);
   nTrain=int(len(examples)*split_ratios[0]);
   nVal=int(len(examples)*split_ratios[1]);
   nTest=len(examples)-nTrain-nVal;

   train_set=examples[0:nTrain];
   val_set=examples[nTrain:nTrain+nVal];
   test_set=examples[nTrain+nVal:];

   train=my_unzip2(train_set)
   val=my_unzip2(val_set)
   test=my_unzip2(test_set)

   return (train, val,  test)


def save_dataset(saveto_dir,all_features,feature_schema,all_examples,gt_quality):
  prefix="data"
  AG_write_attr_file(saveto_dir,prefix,feature_schema)

  random.seed(1234);

  datasets=split_dataset([0.5,0.25,0.25],all_features,all_examples)

  for ds,set_name in zip(datasets,['train','valid','test']):
    AG_save_dataset(saveto_dir,prefix,set_name,ds[0],feature_schema,ds[1],gt_quality)



def load_name_map(names):
  with open(names,'r') as fNames:
    return yaml.load(fNames)

def filter_boxes_in_place(example_boxes,name_map):
  i=0
  while i<len(example_boxes):
    b=example_boxes[i]
    if b.name not in name_map:
      print "Removing", b.name
      del example_boxes[i];
    else:
      i+=1;
      new_name=name_map[b.name]
      if b.name != new_name:
        b.name=new_name



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
    gt_quality=compute_gt_quality(all_examples,gold_standard_session,name_map)
  else:
    gt_quality=None

  (all_features,feature_schema)=extract_all_features(all_examples,name_map)

  save_dataset(saveto_dir,all_features,feature_schema,all_examples,gt_quality)
    


    

if __name__ == "__main__":
  main(sys.argv, sys.stdout, os.environ)
