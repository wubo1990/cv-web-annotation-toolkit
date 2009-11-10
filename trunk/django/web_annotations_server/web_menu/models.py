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

from django.db import models
from django.conf import settings
import os

class Menu(models.Model):
	code   = models.SlugField();
	title  = models.TextField(blank=True,default="")
	active = models.BooleanField(default=False)

	def __str__(self):
        	return self.code

	class Admin:
		pass
	def img_dir(self):
		d = os.path.join(settings.WEBMENU_ROOT,'menus',self.code)
		if not os.path.exists(d):
			os.makedirs(d)
		return d

	def available_items(self):
		if 0==1:
			filenames=os.listdir(self.img_dir());
			drinks = []
			for filename in filenames:
				if filename.endswith(".jpg"):
					d,c=MenuItem.objects.get_or_create(menu=self,image_name=filename)
					drinks.append(d)
			return drinks
		else:
			return self.menuitem_set.filter(available=True)

class MenuItem(models.Model):
	menu        = models.ForeignKey(Menu);
	image_name  = models.TextField(blank=True)
	metadata    = models.TextField(blank=True)
	base_pose   = models.TextField(blank=True)
	object_pose = models.TextField(blank=True)
	available   = models.BooleanField(default=True)

	def __str__(self):
        	return self.metadata+"["+self.image_name+"]";

ORDER_STATE = (
            (1, 'Incomplete'),
            (2, 'Submitted'),
            (3, 'Active'),
            (4, 'Rejected'),
            (5, 'Served'),
            (6, 'Aborted'),
            (10, 'Hidden'),
            (15, 'ServedHidden'),
        )        

class Order(models.Model):
	item        = models.ForeignKey(MenuItem,blank=True,null=True);
	
	delivery_location    = models.TextField(blank=True)
	tip         = models.DecimalField(max_digits=15,decimal_places=4,
					       default="0.0",
					       help_text="The tip to speed the maybe bump the priority up.");

	user_name   = models.TextField(blank=True)
	
	ETA_seconds = models.DecimalField(max_digits=15,decimal_places=4,
					       default="-1.0");
	queue_position = models.IntegerField(blank=True,default="-1");
	server      = models.ForeignKey('Server',blank=True,null=True);
	state       = models.IntegerField(choices=ORDER_STATE,default=1);

	image_name  = models.TextField(blank=True)


	
	metadata    = models.TextField(blank=True)

	def __str__(self):
		return "%d(%d)" % (self.id,self.state)

	def ETA_minutes(self):
		if self.ETA_seconds==-1:
			return -1
		else:
			return float(self.ETA_seconds)/60.0;

	def get_delivery_location_name(self):
		delivery_location_name=WorldStation.objects.get(location=self.delivery_location).code.replace('_',' '); 
		return delivery_location_name


class Server(models.Model):
	code      = models.SlugField()
	name      = models.TextField(blank=True)
	pic       = models.TextField(blank=True)
	def __str__(self):
		return "%s [%s]" %(self.name,self.code)

class Map(models.Model):
	code      = models.SlugField()
	image     = models.TextField(blank=True)
	frame_id  = models.TextField(blank=True)
	cell_size = models.DecimalField(max_digits=15,decimal_places=4,
					       default="0.0");
	def __str__(self):
		return "%s [%s @ %s]" %(self.code,self.image,self.cell_size)


class WorldStation(models.Model):
	code      = models.SlugField()
	image     = models.TextField(blank=True)
	location  = models.TextField(blank=True)
	world_map = models.ForeignKey(Map)

	def __str__(self):
		return "%s [%s @ %s]" %(self.code,self.location,self.world_map.code)

	
class ServiceDomain(models.Model):
	code      = models.SlugField()
	servers   = models.ManyToManyField(Server)
	map       = models.ForeignKey(Map)
	menus     = models.ManyToManyField(Menu)
	title     = models.TextField()

