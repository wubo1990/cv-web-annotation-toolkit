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


DEFAULT_MENU_CODE='drinks'
MENU_DESIGN='iphone';

design_templates={
	'plain':{'new_order':'web_menu/new_order.html',
		 'stats':'web_menu/stats.html',
		 'order_review':'web_menu/my_order.html',
		 'my_order':'web_menu/my_order.html',
		 
		 },
	'iphone':{'new_order':'web_menu/iphone/new_order.html',
		  'stats':'web_menu/iphone/stats.xml',
		  'order_review':'web_menu/iphone/my_order.xml',
		  'my_order':'web_menu/iphone/my_order.html',
		  }
	};

design=design_templates[MENU_DESIGN];



def index(request):
    return HttpResponse("Ash nazg durbatuluk, ush nazg gimbatul, ash nazg thrakatuluk, agh burzum-ishi krimpatul")



def wait(request,menu_code="default"):
	menu,created=Menu.objects.get_or_create(code=menu_code)
	print "Serving root page"
	return render_to_response('web_menu/menu.html',{'menu':menu})


def start(request):
	print "START"
	if 'order_id' in request.session:
		print "Has session"
		try:
			print "Session order ID is",request.session['order_id']
			order=Order.objects.get(id=request.session['order_id']);
			if order.state != 1 and order.state<4:
				return HttpResponseRedirect("/web_menu/order/show/%d/#_Order/%d" % (order.id,order.id))
		except:
			return HttpResponseRedirect("/web_menu/order/new/")
	
	return HttpResponseRedirect("/web_menu/order/new/")



def show_order(request,order_id):
	order=Order.objects.get(id=order_id)
	if MENU_DESIGN=="iphone":
		if 'Mozilla' in request.META['HTTP_USER_AGENT']:
			is_firefox=1;
		else:
			is_firefox=0;
		return render_to_response(design['new_order'], {'order':order,'menu':[],'map':[],'server':[],'info':[],'is_firefox':is_firefox})
	else:
		return render_to_response('web_menu/my_order.html', {'order':order})


def get_order_xml(request,order_id=None):
	if not order_id:
		order_id=request.REQUEST['order_id'];

	order=Order.objects.get(id=order_id)
	if "order_id" in request.session and order.id==int(request.session['order_id']):
		order.my_order = 1;
	else:
		order.my_order = 0; 
	print order.my_order,order.id

	return render_to_response('web_menu/iphone/order.xml', {'order':order,'target':'order-content'},mimetype='text/xml');


def my_order_xml(request):
	order_id=request.session['order_id'];
	order=Order.objects.get(id=order_id)
	order.my_order=1;

	return render_to_response('web_menu/iphone/order.xml', {'order':order,'target':'ordered-content','goto':'waOrdered'},mimetype='text/xml');






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






def get_info_stats(server):
	num_orders=0;
	ETA_time=-1;
	num_unknown_times=0;
	for o in server.order_set.filter(state__in=[2,3]):
		num_orders+=1;
		if ETA_time<o.ETA_minutes():
			ETA_time=o.ETA_minutes();
		else:
			num_unknown_times+=1
	if ETA_time<0:
		ETA_time = 0;

	ETA_time += num_unknown_times * 2;

	info_stats={'queue_length':num_orders,'ETA_time':ETA_time};
	return info_stats

def new_order(request):
	print request
	domain_code='intel'
	domain=get_object_or_404(ServiceDomain,code=domain_code);


	server=domain.servers.all()[0];

	menu = domain.menus.all()[0]

	order = None

	if 'order_id'  in request.session:
		order=get_object_or_404(Order,id=request.session['order_id']);
		if order.state>3:
			order=None;
			del request.session['order_id'];

	if order is None:
		order=Order(state=1,server=server);
		order.save();
		request.session['order_id']=order.id;

	info_stats=get_info_stats(server);

	if 'Mozilla' in request.META['HTTP_USER_AGENT']:
		is_firefox=1;
	else:
		is_firefox=0;
	if order.state > 1:
		order.is_not_new = True

	return render_to_response(design['new_order'], {'order':order,'menu':menu,'map':domain.map,'server':server,'info':info_stats,'is_firefox':is_firefox})


def new_order_submit_full(request):
	print request
	order=None
	if 'order_id' in request.session:
		try:
			order=Order.objects.get_object(id=request.session['order_id']);
			if order.state != 1: # the current order is not new
				order=None
		except:
			order=None
	if not order:
		domain_code='intel'
		domain=get_object_or_404(ServiceDomain,code=domain_code);
		
		server=domain.servers.all()[0];

		menu = domain.menus.all()[0]
	
		order=Order(state=1,server=server);
		order.save();
		request.session['order_id']=order.id;

	order.delivery_location=request.REQUEST['stationSelector'];
	order.user_name=request.REQUEST['personname'];
	order.item=get_object_or_404(MenuItem,id=request.REQUEST['drinkSelector']);
	order.state=2 #ready
	order.save();

	sent = send_order(order)
	print "Sent:",sent
	order.my_order = 1;

	return render_to_response('web_menu/iphone/order.xml', {'order':order,'target':'waOrdered','goto':'waOrdered' },mimetype='text/xml');	


	
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


def choose_order_delivery_station(request,order_id,map_id,station_code):
	order=get_object_or_404(Order,id=order_id);
	world_map=get_object_or_404(Map,id=map_id);
	
	order.delivery_location=station_code;
	order.save();

	return HttpResponse("+")


	
def order_set_tip(request,order_id):
	tip=request.REQUEST['tip']
	order=get_object_or_404(Order,id=order_id);
	order.tip=tip;
	order.save();

	return HttpResponse("+")

def order_set_user_name(request,order_id):
	user_name=request.REQUEST['user_name']
	order=get_object_or_404(Order,id=order_id);
	order.user_name = user_name;

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
def order_cancel(request,order_id):
	order=get_object_or_404(Order,id=order_id);
	if order.state!=3: #active
		order.state=6; #aborted
		order.save();
		#return HttpResponse("+")
	#return HttpResponse("-")
	if 'order_id' in request.session:
		del request.session['order_id']
	return render_to_response("web_menu/iphone/cancel.xml",{'order':order,'target':'order-content'},mimetype='text/xml');

	
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
		if int(new_state)>order.state:
			order.state=int(new_state);

	order.save();

	return HttpResponse("+");




def resend_orders(request):
	server_code=request.REQUEST["server"];
	server=get_object_or_404(Server,code=server_code);	
	for order in server.order_set.filter(state__in=[2,3]):
		sent=send_order(order);

	return HttpResponse("+");



def service_stats(request):
	print request
	domain_code='intel'
	domain=get_object_or_404(ServiceDomain,code=domain_code);

	server=domain.servers.all()[0];

	all_orders=server.order_set.filter(state=5) #served only orders
	all_counts={};
	total = 0;
	for o in all_orders:
		name=o.item.metadata;
		if name in all_counts:
			all_counts[name]=all_counts[name]+1;
		else:
			all_counts[name]=1;
		total+=1;
	by_drink=[];
	for (k,v) in all_counts.items():
		by_drink.append({'name':k,'count':v});

	info_stats=get_info_stats(server);

	stats={'total_drinks':total,'by_drink':by_drink,'server':info_stats};
	print stats


	return render_to_response(design['stats'], {'stats': stats}, mimetype='text/xml');



def reset_orders(request):
	domain_code='intel'
	domain=get_object_or_404(ServiceDomain,code=domain_code);

	server=domain.servers.all()[0];

	all_orders=server.order_set.filter(state__in=[2,3]) #served only orders
	for o in all_orders:
		o.state=6; #aborted
		o.save();

	return HttpResponse("+");


def hide_served_orders(request,domain_code='intel'):
	domain=get_object_or_404(ServiceDomain,code=domain_code);

	server=domain.servers.all()[0];

	all_orders=server.order_set.filter(state__in=[5]) #served only orders
	for o in all_orders:
		o.state=15; #Served&hidden
		o.save();

	return HttpResponse("+");
