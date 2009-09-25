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





def newImage(request,menu_code="default"):
	menu,created=Menu.objects.get_or_create(code=menu_code)

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

	return HttpResponse("image accepted")


def clearImages(request,menu_code="default"):
	menu=get_object_or_404(Menu,code=menu_code);

	img_dir=menu.img_dir()
	for file in os.listdir(img_dir):
		os.remove(os.path.join(img_dir,file))

	return HttpResponse("all gone!")











