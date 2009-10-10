#!/usr/bin/env python
# Do this before running
#export DJANGO_SETTINGS_MODULE=web_annotations_server.settings

from django.contrib.sites.models import Site

import os,sys,time,shutil,getopt, random

from cv_models.models import *
from django.conf import settings

import cv_models.pf_hog.training
import cv_models.sfm_3dmodel.training

import session_results_VOC

"""
usage: %(progname)s [--model=model_id]

  * Build all models as needed.
  * --model=model_id - build a single model and exit
  
"""

def writeError(report,msg):
    fError=open(report+'.error','a')
    print >>fError,msg
    fError.close()

def writeMessage(report,msg):
    fError=open(report,'a')
    print >>fError,msg
    fError.close()    


def ensure_dir(d):
    if not os.path.exists(d):
        os.makedirs(d)

def prepare_data(m):
    if m.model_type==1: # PF-HOG
        return cv_models.pf_hog.training.prepare_data(m)

    elif m.model_type==4: #3D feature cloud by Alvaro Collet
        return cv_models.sfm_3dmodel.training.prepare_data(m)

        
    return False


pf_object_detector_rt='/home/sorokin2/ros/ros-pkg/sandbox/pf_object_detector'


def build_model(m):
    if m.model_type==1: # PF-HOG
        cv_models.pf_hog.training.build_model(m)

    elif m.model_type==4: #3D feature cloud by Alvaro Collet
        cv_models.sfm_3dmodel.training.build_model(m)

def test_model(m):
    model_root=m.location;
    data_root=os.path.join(model_root,'data');
    ensure_dir(data_root)

    if m.model_type==1: # PF-HOG
        #m.model_status=3; #Testing 
        #m.save();
        
        models_dir=os.path.join(model_root,'models');
        ensure_dir(models_dir)
        local_dir=os.path.join(data_root,'local/model-%d-ds' % m.id);
        ensure_dir(local_dir)
        results_dir=os.path.join(data_root,'results/model-%d-ds' % m.id);

        num_targets_ready=0
        for target in m.targets.all():
            target_class=target.target_code;
            model_fn=os.path.join(local_dir,'cache',target_class+"_final.mat");
            model_final_fn=os.path.join(models_dir,target_class+".mat");
            print model_final_fn
            print model_fn

            done_fn=os.path.join(model_root,'models',target_class+'.test.done.txt');
            if os.path.exists(done_fn):
                num_targets_ready += 1
                continue
            
            cmd="rosrun pf_object_detector run_pf_pascal.sh " + \
                 ("%s/ " % settings.MCR_ROOT)+ \
                 target_class + " " + \
                 m.model_arguments + " " + \
                 "%s/  " % data_root + \
                 "1 1"
            print cmd
            sts=os.system(cmd)

            #if not os.path.exists(model_fn):
            #    return False

            #shutil.copy(model_fn,model_final_fn);
            
            fDone=open(done_fn,'w')
            print >>fDone,time.strftime('%X %x %Z')
            fDone.close();
            num_targets_ready += 1

        if num_targets_ready == m.targets.count():
            m.model_status=301; #Learning complete
            m.save()
        
        
def run_training(model_id=None):
    if model_id:
        allmodels=LearnedModel.objects.filter(id=model_id);
    else:
        allmodels=LearnedModel.objects.filter(model_status__in=[2,3]);
        
    for m in allmodels:
        if m.model_status == 2: #"learning"
            action="train"
        elif m.model_status == 3: #"testing"
            action="test"
        else:
            action="?"

            
        if action=="train":
            isOK=prepare_data(m)
            if not isOK:
                continue
            
            isOK=build_model(m)
            if not isOK:
                continue

        if action=="test":
            isOK=test_model(m)
            if not isOK:
                continue
            


def run_training_cycle():
    while True:
        #try:
        run_training();
        #except:
        print "Mysterious error while running all training"            
        time.sleep(5)
        print time.localtime()


def usage(progname):
  print __doc__ % vars()

if __name__=="__main__":
    
    progname = sys.argv[0]
    optlist, args = getopt.getopt(sys.argv[1:], "", ["help", "model="])

    model_id=None
    mode="continuous";
            
    for (field, val) in optlist:
        if field == "--help":
            usage(progname)
            sys.exit()
        elif field == "--model":
            model_id=int(val)
            mode="single_model";

    if mode=="continuous":
        run_training_cycle();
    elif mode=="single_model":
        run_training(model_id);
    else:
        print "Unknown model ID", model_id
