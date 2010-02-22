#!/usr/bin/env python
# Copyright (c) 2009, Willow Garage, Inc.
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Willow Garage, Inc. nor the names of its
#       contributors may be used to endorse or promote products derived from
#       this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

# Author: Alexander Sorokin. 
from __future__ import with_statement

PKG='crowd_quality'
import roslib; roslib.load_manifest(PKG)

import unittest

import sys,os
import subprocess
from xml.dom import minidom

from crowd_quality.bbox import *
from crowd_quality.bbox.generate_bbox_dataset import *
from cv_mech_turk2.tasks.boxes import *
from cv_mech_turk2.session_results import *

## Test session_results
class TestBBoxOverlap(unittest.TestCase):

    ## import everything
    def test_bbox_overlap(self):
        bb1=BoundingBox(10,10,30,30);
        bb2=BoundingBox(20,20,40,10);
        boxes1=[bb1,bb2];
        bb1=BoundingBox(13,13,27,35);
        bb2=BoundingBox(22,19,25,10);
        boxes2=[bb1,bb2];
        print compute_bbox_set_agreement(boxes1,boxes2)

    def get_test_data_dir(self):
        p=subprocess.Popen("rospack find crowd_quality",stdout=subprocess.PIPE,shell=True)
                              
        (stdoutdata, stderrdata) = p.communicate();
        package_dir=stdoutdata.strip()    
        data_dir=os.path.join(package_dir,"test_data");
        return data_dir

    def test_agreement(self):        

        data_dir=self.get_test_data_dir()

        x_gold=minidom.parse(os.path.join(data_dir,"test_02","gold.xml"))
        x_submission=minidom.parse(os.path.join(data_dir,"test_02","submission.xml"))
        score1 = agreement.compute_agreement(x_submission,x_gold)
        self.assertTrue(score1<0.10)
        score2 = agreement.compute_agreement(x_gold,x_submission)
        self.assertTrue(score2<0.10)
        self.assertAlmostEqual(score1,score2,0.001)

        x_gold=minidom.parse(os.path.join(data_dir,"test_02","gold2.xml"))
        x_submission=minidom.parse(os.path.join(data_dir,"test_02","submission_to_gold2.xml"))
        score = agreement.compute_agreement(x_submission,x_gold)
        self.assertTrue(score>0.9)


    def x_test_session_results_filter(self):
        
        p=subprocess.Popen("rospack find crowd_quality",stdout=subprocess.PIPE,shell=True)
                              
        (stdoutdata, stderrdata) = p.communicate();
        my_dir=stdoutdata.strip()    

        name_map=load_name_map(os.path.join(my_dir,"test_data","test_01","name_mapping.yaml"))

        gt=SessionResults();
        gt.read_results(os.path.join(my_dir,"test_data","test_01","gt"));

        session1=SessionResults();
        session1.read_results(os.path.join(my_dir,"test_data","test_01","session1"));

        all_submissions={};
        collect_submissions(session1,all_submissions);

        k='2008_002359.jpg';
        k_submissions={k:all_submissions[k]};
        all_examples=create_examples(k_submissions);

        gt_quality=compute_gt_quality(all_examples,gt,name_map)

        for subm,q in gt_quality.items():
            self.assertEqual(q,1)

if __name__ == '__main__':
    import rostest
    rostest.rosrun(PKG, 'test_bbox_overlap', TestBBoxOverlap)

