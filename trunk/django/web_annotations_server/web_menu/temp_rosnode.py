#! /usr/bin/python                                                                                                    

#***********************************************************                                                          
#* Software License Agreement (BSD License)                                                                           
#*                                                                                                                    
#*  Copyright (c) 2009, Willow Garage, Inc.                                                                           
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
# Authors: Ian GoodFellow, Alexander Sorokin

import sys

import roslib
import roslib.scriptutil
roslib.load_manifest('cv_mech_turk')
import rospy
import random
import sys

from std_msgs.msg import String


class TmpNode:
  def __init__(self):
      self.node_name="web_menu_sender"
      rospy.init_node(self.node_name, anonymous=True)

      self.drink_topic="/drink"
      self.drink_pub=rospy.Publisher(self.drink_topic,String)
      self.drink_topic_type='std_msgs/String'

  def send_drink_id(self,drink_id):
	self.drink_pub.publish(drink_id)

  def get_pub_string(self):
      print "HERE"
      return "%s,%s,%s,%s" % (self.node_name,self.drink_topic,self.drink_topic_type,rospy.get_node_uri())
      

if __name__=="__main__":
    n=TmpNode();
    print n.get_pub_string();

