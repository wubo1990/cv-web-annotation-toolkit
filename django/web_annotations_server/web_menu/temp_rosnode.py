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
roslib.load_manifest('web_object_menu')
import rospy
import random
import sys
import pickle

from std_msgs.msg import String
import geometry_msgs.msg
from web_object_menu.msg import Order


class TmpNode:
  def __init__(self):
      self.node_name="web_menu_sender"
      rospy.init_node(self.node_name, anonymous=True)

      self.drink_topic="/drink"
      self.drink_pub=rospy.Publisher(self.drink_topic,String)
      self.drink_topic_type='std_msgs/String'

      self.orders_topic="/order"
      self.orders_pub=rospy.Publisher(self.orders_topic,Order)
      self.orders_topic_type='web_object_menu/Order'

  def send_drink_id(self,drink_id):
	self.drink_pub.publish(drink_id)

  def send_order(self,order,map,x,y):
      print dir(order)
      print order.id
      msgO=Order();
      msgO.order_id=str(order.id);
      msgO.tip=float(order.tip);
      #msgO.delivery_pose.header.frame_id=str(map.frame_id);
      #msgO.delivery_pose.pose.position.x=x;
      #msgO.delivery_pose.pose.position.y=y;
      msgO.delivery_pose.pose.position.z=0;
      msgO.delivery_pose.pose.orientation.x=0;
      msgO.delivery_pose.pose.orientation.y=0;
      msgO.delivery_pose.pose.orientation.z=0;
      msgO.delivery_pose.pose.orientation.w=1;

      #grab_base_pose=geometry_msgs.msg.PoseStamped()
      #s=str(pickle.loads(str(order.item.base_pose)))
      #grab_base_pose.deserialize(s)

      msgO.delivery_location=str(order.delivery_location);
      msgO.object_approach_location=str(order.item.base_pose);
      msgO.object_type=str(order.item.object_pose);

      #msgO.object_approach_pose = grab_base_pose
      
      self.orders_pub.publish(msgO)
      self.drink_pub.publish("%s %s" % (str(order.item.base_pose),str(order.delivery_location)));

  def get_pub_string(self):
      s1= "%s,%s,%s,%s" % (self.node_name,self.drink_topic,self.drink_topic_type,rospy.get_node_uri())
      #s1= "%s,%s,%s" % (self.node_name,self.drink_topic,rospy.get_node_uri())
      s2= "%s,%s,%s,%s" % (self.node_name,self.orders_topic,self.orders_topic_type,rospy.get_node_uri())
      #return s1
      return s1+"\n"+s2
      

if __name__=="__main__":
    n=TmpNode();
    print n.get_pub_string();

