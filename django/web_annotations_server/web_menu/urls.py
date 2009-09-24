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

import views
from django.conf import settings

urlpatterns = patterns('',
    (r'^$', 'web_menu.views.wait'),
    (r'^m/(?P<menu_code>[\w-]+)/$', 'web_menu.views.wait'),
    (r'^images/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.WEBMENU_ROOT+'menus/'}),

    (r'^menu/?$', 'web_menu.views.show_drink_menu'),
    (r'^menu//?$', 'web_menu.views.show_drink_menu'),
    (r'^menu/(?P<menu_code>[\w-]+)/?$', 'web_menu.views.show_drink_menu'),

    (r'^choose_drink/(?P<menu_code>[\w-]+)/(?P<drink_name>.*)$', 'web_menu.views.made_selection'),
    (r'^choose_drink(?P<drink_name>[^/]*)$', 'web_menu.views.made_selection'),
    (r'^newImage/$','web_menu.views.newImage'),
    (r'^newImage/(?P<menu_code>.*)/$','web_menu.views.newImage'),
    (r'^clearImages/$','web_menu.views.clearImages'),
    (r'^clearImages/(?P<menu_code>[\w-]+)/$','web_menu.views.clearImages'),
    (r'^enableMenu/$','web_menu.views.enableMenu'),
    (r'^enableMenu/(?P<menu_code>[\w-]+)/$','web_menu.views.enableMenu'),

    (r'^all/$','web_menu.views.all_menus'),

)
