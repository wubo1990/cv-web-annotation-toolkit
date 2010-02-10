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
# Authors: Alexander Sorokin


import roslib; roslib.load_manifest('mech_turk_ros') #django_crowd_server
import rospy

import sys,pickle

from std_msgs.msg import String
from mech_turk_ros_msgs.msg import ExternalAnnotation


class PublishAnnotationNode:
    def __init__(self,node_name):
        self.node_name=node_name


        self.annotation_topic="/django_crowd_server/annotation"
        self.annotation_pub=rospy.Publisher(self.annotation_topic,ExternalAnnotation)
        self.annotation_topic_type='mech_turk_ros_msgs/ExternalAnnotation'

    def send_annotation(self,annotation_xml,uid):

        anntoation_msg = ExternalAnnotation();
        anntoation_msg.uid = uid;
        anntoation_msg.image_reference.uid = uid;
        self.annotation_pub.publish(anntoation_msg)


    def get_publishers_info(self):
      s1= {"node":self.node_name,"topic":self.annotation_topic,"topic_type":self.annotation_topic_type,"publisher_url":rospy.get_node_uri()}
      return [s1]

      

if __name__=="__main__":
    n=AnnotationPublisherNode();
    print n.get_pub_string();

