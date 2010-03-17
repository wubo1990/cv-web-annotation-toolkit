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

from django.conf.urls.defaults import *

from models import *
import views
from django.conf import settings
from django.views.generic import list_detail

active_orders_list_info = {
    'queryset' :   Order.objects.all().filter(state__in=[2,3]).order_by('-state','queue_position'),
    'allow_empty': True,
}
active_orders_list_info_xml = {
    'queryset' :   Order.objects.all().filter(state__in=[2,3]).order_by('-state','queue_position'),
    'allow_empty': True,
    'template_name':'web_menu/iphone/order_list.xml',
    'mimetype' : 'text/xml',
}



urlpatterns = patterns('',
    #(r'^$', 'web_menu.views.wait'),
    (r'^$', 'web_menu.views.start'),

                       
    (r'^m/(?P<menu_code>[\w-]+)/$', 'web_menu.views.wait'),
    (r'^s/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.DJ_CODE_RT+'web_menu/html/'}),                       
    (r'^images/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.WEBMENU_ROOT+'menus/'}),
    (r'^map_images/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.WEBMENU_ROOT+'maps/'}),
    (r'^server_images/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.WEBMENU_ROOT+'servers/'}),

    (r'^menu/?$', 'web_menu.views.show_drink_menu'),
    (r'^menu//?$', 'web_menu.views.show_drink_menu'),
    (r'^menu/(?P<menu_code>[\w-]+)/?$', 'web_menu.views.show_drink_menu'),

    (r'^choose_drink/(?P<menu_code>[\w-]+)/(?P<drink_name>.*)$', 'web_menu.views.made_selection'),
    (r'^choose_drink(?P<drink_name>[^/]*)$', 'web_menu.views.made_selection'),
    (r'^newImage/$','web_menu.views.new_image'),
    (r'^newImage/(?P<menu_code>.*)/$','web_menu.views.new_image'),
    (r'^clearImages/$','web_menu.views.clearImages'),
    (r'^clearImages/(?P<menu_code>[\w-]+)/$','web_menu.views.clearImages'),
    (r'^enableMenu/$','web_menu.views.enableMenu'),
    (r'^enableMenu/(?P<menu_code>[\w-]+)/$','web_menu.views.enableMenu'),

    (r'^all/$','web_menu.views.all_menus'),
    (r'^rospublishers/$','web_menu.views.get_ros_publishers'),

    (r'^queue/$',list_detail.object_list, active_orders_list_info),
    (r'^queue.xml$',list_detail.object_list, active_orders_list_info_xml),

    (r'^stats.xml$','web_menu.views.service_stats'),

    (r'^myorder.xml$','web_menu.views.my_order_xml'),
    (r'^order/xml/$','web_menu.views.get_order_xml'),
    (r'^order/xml/(?P<order_id>[\w-]+)/$','web_menu.views.get_order_xml'),

    #(r'^queue/$',list_detail.object_list, active_orders_list_info),
    #(r'^queue.xml$',list_detail.object_list, active_orders_list_info_xml),                       
                       
    #(r'^queue/server/(?P<server_code>)/$','web_menu.views.show_queue'),
    #(r'^queue/service/(?P<service_domain>)/$','web_menu.views.show_domain_queue'),

    (r'^order/new/$',views.new_order),
    (r'^order/new/submit',views.new_order_submit_full),
    (r'^order/choose_item/(?P<order_id>[\w-]+)/(?P<item_id>[\w-]+)/$',views.choose_order_item),
    (r'^order/deliver_to/(?P<order_id>[\w-]+)/(?P<map_id>[\w-]+)/$',views.choose_order_map_location),
    (r'^order/deliver_to_station/(?P<order_id>[\w-]+)/(?P<map_id>[\w-]+)/(?P<station_code>[\w-]+)/$',views.choose_order_delivery_station),
    (r'^order/tip/(?P<order_id>[\w-]+)/$',views.order_set_tip),
    (r'^order/user_name/(?P<order_id>[\w-]+)/$',views.order_set_user_name),
    (r'^order/confirm/(?P<order_id>[\w-]+)/$',views.order_confirm),
    (r'^order/cancel/(?P<order_id>[\w-]+)/$',views.order_cancel),

    (r'^order/show/(?P<order_id>[\w-]+)/$',views.show_order),                       

    (r'^order/update/$',views.update_order),
    (r'^order/resend/$',views.resend_orders),

    (r'^reset/$',views.reset_orders),                       
    (r'^hide/served$',views.hide_served_orders),                       

)
