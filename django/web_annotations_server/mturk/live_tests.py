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

import sys,os
import unittest
import uuid

from django.conf import settings

TEST_SERVER_DOMAIN='vm6.willowgarage.com:8080'
TEST_USER='mt_tester'
TEST_PWD='3846a41e-5642-4539-859d-8775920af197'

import xmlrpclib, httplib
"""
+ list_sessions
+ list_session_work_units
from rpc import list_work_unit_submissions


from rpc import get_session
+ from rpc import get_session_work_units
+ from rpc import get_work_unit_submissions


+ create_session
+ copy_session
+ create_work_unit
from rpc import submit_work
from rpc import submit_grade

"""

from xmlrpclib import ServerProxy,Binary

def get_rpc_server():
    return "http://%s:%s@%s/RPC2" % (TEST_USER,TEST_PWD,TEST_SERVER_DOMAIN)

class TestRPC(unittest.TestCase):

    def generate_session_id(self,prefix):
        rand_id=str(uuid.uuid4())
        return prefix+"-"+rand_id

    def generate_image_id(self,prefix=None):
        rand_id=str(uuid.uuid4())
        if prefix:
            return prefix+"-"+rand_id
        else:
            return rand_id

    def generate_id(self,prefix=None):
        rand_id=str(uuid.uuid4())
        if prefix:
            return prefix+"-"+rand_id
        else:
            return rand_id

    ## import everything
    def test_basics(self):
        
        #t = AuthTransport()
        #s = ServerProxy(get_rpc_server(),transport=t)
        s = ServerProxy(get_rpc_server())

        methods=s.system.listMethods()
        self.assert_("mt.list_session_work_units" in methods)

        my_sessions=s.mt.list_sessions();
        print my_sessions

        self.assert_("test-bbox-session-prototype" in my_sessions)
        self.assert_("test-outline-session-prototype" in my_sessions)

        box_session=self.generate_session_id('test-bbox');
        s.mt.copy_session('test-bbox-session-prototype',box_session);

        my_sessions2=s.mt.list_sessions();
        self.assert_(box_session not in my_sessions);
        self.assert_(box_session in my_sessions2);

        box_session2=self.generate_session_id('test-bbox');
        new_session_id = s.mt.create_session(box_session2,'test-bbox','Internal','blank',7,[]);
        self.assertEqual(box_session2,new_session_id);

        my_sessions3=s.mt.list_sessions();
        self.assert_(box_session2 in my_sessions3);

        img_file_name=os.path.join(settings.MTURK_TEST_DATA,'image_0001.jpg')
        img_file=open(img_file_name,'rb');
        img=img_file.read();
        remote_image_name=self.generate_image_id()
        s.mt.post_image(box_session,xmlrpclib.Binary(img),remote_image_name+".jpg"); # ,'image_0001.jpg')

        parameters="frame=%s&original_name=imgae_0001.jpg" %(remote_image_name);
        new_work_unit_id = s.mt.create_work_unit(box_session,parameters,False);
        
        box_session_work_units=s.mt.list_session_work_units(box_session);
        self.assert_(new_work_unit_id in box_session_work_units);

        work_units=s.mt.get_session_work_units(box_session);
        self.assertEqual(work_units[0]['id'],         new_work_unit_id)
        self.assertEqual(work_units[0]['state'],      'Idle')
        self.assertEqual(work_units[0]['session'],    box_session)
        self.assertEqual(work_units[0]['submissions'],[])



        submission_data={'load_time':'Sunday, January 24 2010 01:35 AM',
                    'submit_time':'Sunday, January 24 2010 01:40 AM',
                    'sites':"""<?xml version="1.0"?>
<results>
<image url="http://%s/frames/%s/%s.jpg"/>
<annotation>
<size>
<width>640</width>
<height>480</height>
</size>
<bbox height="132" left="285.1" name="object" sqn="1" top="114.4" width="51.2">
<pt ct="1264315826499" x="285.1" y="114.4"/>
<pt ct="1264315831993" x="336.3" y="246.4"/>
</bbox>
</annotation>
<meta load_time="1264315821239" submit_time="1264315843336"/>
</results>
""" %(TEST_SERVER_DOMAIN, box_session, remote_image_name),
                    'Comments':'Test comments'};

        test_worker_id=self.generate_id('test_worker')
        assignment_id = self.generate_id('test-assignment-1');
        submission_id = s.mt.submit_work(new_work_unit_id,test_worker_id,assignment_id,submission_data)

        work_units2=s.mt.get_session_work_units(box_session);
        
        self.assertEqual(len(work_units2[0]['submissions']),1)
        self.assertEqual(work_units2[0]['submissions'][0],submission_id)

        submissions = s.mt.get_work_unit_submissions(new_work_unit_id)

        self.assertEqual(submissions[0]['id'] ,submission_id)

        test_worker_id_2= self.generate_id('test_worker')
        assignment_id_2 = self.generate_id('test-assignment-1');
        submission_id_2 = s.mt.submit_work(new_work_unit_id,test_worker_id_2,assignment_id_2,submission_data)

        submissions = s.mt.get_work_unit_submissions(new_work_unit_id)
        self.assertEqual(len(submissions),2)

        self.assertEqual(len(submissions),2)



if __name__ == '__main__':
    unittest.main()


