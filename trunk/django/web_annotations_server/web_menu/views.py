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

import urllib,uuid,os,sys,shutil,subprocess

from django.conf import settings

from django.http import HttpResponse,Http404,HttpResponseRedirect
from django.shortcuts import render_to_response,get_object_or_404 
from django.views.generic.list_detail import object_list
from django.core.files.storage import FileSystemStorage

from django.contrib.auth.decorators import login_required

from models import *


try:
	from web_menu.temp_rosnode import TmpNode
	ros_sender=TmpNode();
except:
	cached_exception = [ str(sys.exc_type), str(sys.exc_value)]
	ros_sender=None

#Comment out to allow ros integration
#ros_sender=None

def get_ros_publishers(request):
    if not ros_sender:
        return HttpResponse("none")
    else:
        s=ros_sender.get_pub_string();
        return HttpResponse(s)





def index(request):
    return HttpResponse("Ash nazg durbatuluk, ush nazg gimbatul, ash nazg thrakatuluk, agh burzum-ishi krimpatul")



def wait(request,menu_code="default"):
	menu,created=Menu.objects.get_or_create(code=menu_code)
	print "Serving root page"
	return render_to_response('web_menu/menu.html',{'menu':menu})




def enableMenu(request,menu_code="default"):
	menu,created=Menu.objects.get_or_create(code=menu_code)
	menu.active=True;
	menu.save()

	if menu_code=="default" or menu_code=="demo":
		demo_rt=os.path.join(settings.WEBMENU_ROOT,'demo_images');
		shutil.copy(os.path.join(demo_rt,'fixed1.jpg'),menu.img_dir());
		shutil.copy(os.path.join(demo_rt,'fixed2.jpg'),menu.img_dir());
		shutil.copy(os.path.join(demo_rt,'fixed3.jpg'),menu.img_dir());

	return HttpResponse("The menu is now available")
def all_menus(request):
	menus=Menu.objects.all();
	return render_to_response('web_menu/all_menus.html',{'menus':menus});

def made_selection(request, drink_name,menu_code="default"):
	menu,created=Menu.objects.get_or_create(code=menu_code)
	#menu.active=False;
	#menu.save()

	#os.remove('/var/datasets/menu/'+drink_name);
	if ros_sender:
		ros_sender.send_drink_id(str(drink_name))
		return render_to_response('web_menu/selection_done.html',{'menu':menu,'drink':drink_name})

	else:
		return render_to_response('web_menu/selection_done.html',{'menu':menu,'drink':drink_name})
		rval = "Error: ros_sender is null due to "
		for info in cached_exception:
			rval = rval + info
		return HttpResponse(rval)
	

def show_drink_menu(request,menu_code="default"):
	menu,created=Menu.objects.get_or_create(code=menu_code)
	if not menu.active:
		return HttpResponse("")

	class Drink:
		def __init__(self,name):
			self.name = name;

	filenames=os.listdir(menu.img_dir());
        drinks = []
        for filename in filenames:
		if filename.endswith(".jpg"):
			drinks.append(Drink(filename))
	
	return render_to_response('web_menu/menu_select.html', {'menu':menu,'drinks':drinks})





def new_image(request,menu_code="default"):
	menu,created=Menu.objects.get_or_create(code=menu_code)

	print request.REQUEST.items()
	frame = request.REQUEST['frame']
	try:
		original_name = request.REQUEST['original_name']
	except KeyError:
		original_name = frame

	original_name = original_name.replace("/","_");
	
	image_dir=menu.img_dir();
        print image_dir

        image=request.FILES['image']
        storage = FileSystemStorage(image_dir);
        path = storage.save(os.path.join(image_dir,original_name),image);

	base_pose = request.REQUEST.get('base_pose','')
	object_pose = request.REQUEST.get('object_pose','')

	mi=MenuItem(menu=menu, image_name=original_name,base_pose=base_pose,object_pose=object_pose);
	mi.save();

	return HttpResponse("ItemID: %d",mi.id)


def clearImages(request,menu_code="default"):
	menu=get_object_or_404(Menu,code=menu_code);

	img_dir=menu.img_dir()
	for file in os.listdir(img_dir):
		os.remove(os.path.join(img_dir,file))

	for mi in menu.menuitem_set.filter(available=True):
		mi.available=False;
		mi.save();

	return HttpResponse("all gone!")



DEFAULT_MENU_CODE='test-menu'

def new_order(request):
	domain_code='default'
	domain=get_object_or_404(ServiceDomain,code=domain_code);


	server=domain.servers.all()[0];

	menu = domain.menus.all()[0]
	
	new_order=Order(state=1,server=server);
	new_order.save();
	request.session['order_id']=new_order.id;

	return render_to_response('web_menu/new_order.html', {'order':new_order,'menu':menu,'map':domain.map,'server':server})


def choose_order_item(request,order_id,item_id):
	menu_code='drinks';
	menu,created=Menu.objects.get_or_create(code=menu_code)

	order=get_object_or_404(Order,id=order_id);
	menu_item=get_object_or_404(MenuItem,id=item_id);
	order.item = menu_item;
	order.save();

	return HttpResponse("+")


def choose_order_map_location(request,order_id,map_id):
	x=request.REQUEST['x']
	y=request.REQUEST['y']
	order=get_object_or_404(Order,id=order_id);
	world_map=get_object_or_404(Map,id=map_id);
	
	order.delivery_location="%s,%s,%s" % (map_id,x,y);
	order.save();

	return HttpResponse("+")

def order_set_tip(request,order_id):
	tip=request.REQUEST['tip']
	order=get_object_or_404(Order,id=order_id);
	order.tip=tip;
	order.save();

	return HttpResponse("+")


def send_order(order):
	print dir(order)
	print order.id
	#(map_id,x,y)=order.delivery_location.split(",")
	#map_id=1;
	#map=get_object_or_404(Map,id=int(map_id));
	#map=get_object_or_404(Map,id=int(map_id));
	#x=float(x) * float(map.cell_size);
	#y=float(y) * float(map.cell_size);
	map=""
	x=""
	y=""

	if ros_sender:
		ros_sender.send_order(order,map,x,y)
		return True
	else:
		return False

def order_confirm(request,order_id):
	order=get_object_or_404(Order,id=order_id);

	tip_s=str(order.tip);
	waiting_orders=Order.objects.filter(state=2).all();
	num_prior_waiting_orders = 0;
	for wo in waiting_orders:
		if wo.tip<= order.tip:
			num_prior_waiting_orders += 1;
		else:
                   wo.queue_position = wo.queue_position+1;
		   wo.save();

	num_active_orders=Order.objects.filter(state=3).count();
	queue_position=num_prior_waiting_orders+num_active_orders+1;

	order.state=2;
	order.ETA_seconds='-1';
	order.queue_position=queue_position;	
	order.save();

	sent=send_order(order);
	if sent:
		return HttpResponse("+");
	else:
		return HttpResponse("-");




def accept_order(request,order_id,ETA="-1"):
	order.state=3;
	order.ETA_seconds=ETA;
	order.save();

	return HttpResponse("+");

def update_order(request,order_id=None,ETA=None,queue_position=None):
	if order_id is None:
		order_id=request.REQUEST["order_id"];

	print request.REQUEST.items()
	order=get_object_or_404(Order,id=order_id);		

	if ETA is None :
		ETA=request.REQUEST.get("ETA",None)

	if ETA is not None :
		order.ETA_seconds=ETA;

	if queue_position is None:
		queue_position=request.REQUEST.get("rank",None)

	if queue_position is not None:
		order.queue_position=queue_position;

	new_state=None;
	if new_state is None:
		new_state=request.REQUEST.get("state",None)
	if new_state is not None:
		order.state=int(new_state);

	order.save();

	return HttpResponse("+");




def resend_orders(request):
	server_code=request.REQUEST["server"];
	server=get_object_or_404(Server,code=server_code);	
	for order in server.order_set.filter(state__in=[2,3]):
		sent=send_order(order);

	return HttpResponse("+");
