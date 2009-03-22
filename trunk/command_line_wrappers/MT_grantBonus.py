#!/usr/bin/python

#*********************************************************************
#* Software License Agreement (BSD License)
#* 
#*  Copyright (c) 2008, University of Illinois at Urbana-Champaign
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
#*   * Neither the name of the University of Illinois nor the names of its
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
#*********************************************************************/
#/****
#* Author: Alexander Sorokin, Department of Computer Science, 
#*                            University of Illinois at Urbana-Champaign.
#* Advised by: David Forsyth.
#* 
#****/ 
#
# Based in part on MTurk SDK code
# Copyright 2007-2008 Amazon Technologies, Inc.
# Obtained under this License: http://aws.amazon.com/apache2.0
##



import os, sys

input_file=sys.argv[1]
if len(sys.argv)>2:
	if sys.argv[2]=='-sandbox':
		sandbox_flag="-sandbox";
	else:
		print "error";
		sys.exit();
else:
	sandbox_flag="";

records=open(input_file,'r').readlines();

wd=os.getcwd();

#mthome=os.getenv('MTURK_CMD_HOME');
#os.chdir(mthome+'/bin/');

print "#!/bin/bash"

print "pushd $MTURK_CMD_HOME/bin/"
for r in records[1:]:
	(assignmentID,workerID,bonus,comment)=r.strip().split('\t')
	cmd="./grantBonus.sh %s -workerid %s -assignment %s -reason %s -amount %s" %(sandbox_flag,workerID,assignmentID,comment,bonus)
	print cmd
	#os.system(cmd);

print "popd"
#os.chdir(wd);
