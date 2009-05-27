﻿/********************************************************************** Software License Agreement (BSD License)**  Copyright (c) 2008, University of Illinois at Urbana-Champaign*  All rights reserved.**  Redistribution and use in source and binary forms, with or without*  modification, are permitted provided that the following conditions*  are met:**   * Redistributions of source code must retain the above copyright*     notice, this list of conditions and the following disclaimer.*   * Redistributions in binary form must reproduce the above*     copyright notice, this list of conditions and the following*     disclaimer in the documentation and/or other materials provided*     with the distribution.*   * Neither the name of the University of Illinois nor the names of its*     contributors may be used to endorse or promote products derived*     from this software without specific prior written permission.**  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS*  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT*  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS*  FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE*  COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,*  INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,*  BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;*  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER*  CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT*  LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN*  ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE*  POSSIBILITY OF SUCH DAMAGE.*********************************************************************//***** Author: Alexander Sorokin, Department of Computer Science,*                                  University of Illinois at Urbana-Champaign.* Advised by: David Forsyth.*****/package vision{	import flash.display.*;	import fl.controls.CheckBox;	import fl.controls.List;	import fl.data.DataProvider;	//import flash.display.Shape;	import fl.controls.Label;	import flash.events.MouseEvent;	import flash.events.Event;	import flash.xml.XMLDocument;	import flash.xml.XMLNode;	import flash.text.*;	import flash.geom.*;	import flash.net.URLLoader;	import flash.net.URLRequest;	import flash.net.URLRequestMethod;	import flash.net.URLLoaderDataFormat;	import flash.display.BitmapData;	import flash.geom.Rectangle;	import flash.utils.ByteArray;	import fl.events.SliderEvent;	import guid.GUID;		dynamic public class SegmentationInput extends MovieClip	{				var pictLdr:Loader;	var targetX=500;	var targetY=500;	var the_image;	var oX;	var oY;	var brush;		var image_base;	var the_video;	var the_frame;	var image_URL;		var m_segmentation_mask;		var m_segmentation_id;			var fg_color;		public function SegmentationInput(server:String=""):void{		image_base=server; //"http://127.0.0.1:8000/";		the_video="demo";		the_frame="000003"		image_URL=image_base+"frames/"+the_video+"/"+the_frame+".jpg"		m_segmentation_id=GUID.create();		brush=m_brush;		m_zoom_control.addEventListener(MouseEvent.MOUSE_DOWN,on_zoom_mouse_down);		m_zoom_control.visible=false;				m_reset_zoom.addEventListener(MouseEvent.CLICK, reset_zoom_button_Click);			m_zoom_btn.addEventListener(MouseEvent.CLICK, zoom_button_Click);		m_zoom_btn.visible=false;		m_reset_zoom.visible=false;				m_btn_done.addEventListener(MouseEvent.CLICK, onBtnDoneClick);		m_save_segmentation_btn.addEventListener(MouseEvent.CLICK, save_segmentation_button_Click);			m_load_segmentation_btn.addEventListener(MouseEvent.CLICK, load_segmentation_button_Click);				m_fg_btn.addEventListener(MouseEvent.CLICK, on_btn_fg);			m_bnd_btn.addEventListener(MouseEvent.CLICK, on_btn_bnd);			m_bg_btn.addEventListener(MouseEvent.CLICK, on_btn_bg);			m_erase_btn.addEventListener(MouseEvent.CLICK, on_btn_erase);							m_brush_size_slider.addEventListener(SliderEvent.CHANGE, announceChange);				 fg_color=(Math.random() % 255) * 0x10000		 +(Math.random() % 255) * 0x100		 +(Math.random() % 255) * 0x1 ;		//fg_color=0xFF0000;				m_brush.set_brush_color(fg_color);		m_brush.set_mode(m_brush.MODE_DRAW);				m_bnd_btn.visible = false;			m_bg_btn.visible=false;		m_save_segmentation_btn.visible=false;			m_load_segmentation_btn.visible=false;				}						function announceChange(e:SliderEvent):void {						m_brush.set_brush_size(e.target.value);		}		function on_mouse_move(event:MouseEvent):void		{			trace(event.localX);						if(event.buttonDown){				var sX=event.stageX;				var sY=event.stageY;				var local_point:Point=m_segmentation_mask.globalToLocal(new Point(sX,sY));				if(local_point.x>=0 && local_point.y>=0 && local_point.x<the_image.width && local_point.y<the_image.height)				{					var ct:ColorTransform=null;					var bm:String=BlendMode.NORMAL;					if(m_brush.get_mode()==m_brush.MODE_ERASE){						bm=BlendMode.ERASE;						//ct=new ColorTransform(0,0,0,-1,0,0,0,0);					}					//the_image.bitmapData.setPixel(local_point.x,local_point.y,0xFFFFFF);					var m:Matrix=new Matrix();					var s:Number=m_brush.height/30;					m.scale(s,s);					m.translate(local_point.x,local_point.y);					m_segmentation_mask.bitmapData.draw(brush,m,ct,bm);									}					}		}		function loaded(event:Event):void		{			var content = event.target.content;					var rW=content.width/targetX;			var rH=content.height/targetY;			var ratio= Math.max(rW,rH);			content.width = content.width/ratio;			content.height = content.height/ratio;			oX=(targetX-content.width)/2;			oY=(targetY-content.height)/2;			content.x = oX;			content.y = oY;			the_image=content;			var bmp=new BitmapData(the_image.bitmapData.width,the_image.bitmapData.height);			m_segmentation_mask=new Bitmap(bmp);			m_sites_holder.addEventListener(MouseEvent.MOUSE_MOVE,on_mouse_move);			m_sites_holder.addChild(m_segmentation_mask);			m_segmentation_mask.x=the_image.x;			m_segmentation_mask.y=the_image.y;			m_segmentation_mask.width=the_image.width;			m_segmentation_mask.height=the_image.height;			var bounds:Rectangle = new Rectangle(0, 0, m_segmentation_mask.bitmapData.width, m_segmentation_mask.bitmapData.height);			m_segmentation_mask.bitmapData.fillRect(bounds,0xFFFFFF);			m_segmentation_mask.alpha=0.8;		}		function set_background_image(image_name:String):void		{			pictLdr=new Loader();						var pictURL:String = image_name;			var pictURLReq:URLRequest = new URLRequest(pictURL);			m_sites_holder.addChild(pictLdr);							pictLdr.contentLoaderInfo.addEventListener(Event.COMPLETE, loaded);			pictLdr.load(pictURLReq);				}				function set_background_image_inline(image):void{			the_image=new Bitmap(image.bitmapData);			m_sites_holder.addChild(the_image);			var rW=the_image.width/targetX;			var rH=the_image.height/targetY;			var ratio= Math.max(rW,rH);			//txtShapeLabel.text= ratio;			//txtShapeLabel.visible=false;			the_image.width = the_image.width/ratio;//the_sites_holder.width;			the_image.height = the_image.height/ratio;//the_sites_holder.height;			oX=(targetX-the_image.width)/2;			oY=(targetY-the_image.height)/2;			the_image.x = oX;			the_image.y = oY;			//the_image=content;			var bmp=new BitmapData(the_image.bitmapData.width,the_image.bitmapData.height);			m_segmentation_mask=new Bitmap(bmp);			m_sites_holder.addEventListener(MouseEvent.MOUSE_MOVE,on_mouse_move);			m_sites_holder.addChild(m_segmentation_mask);			m_segmentation_mask.x=the_image.x;			m_segmentation_mask.y=the_image.y;			m_segmentation_mask.width=the_image.width;			m_segmentation_mask.height=the_image.height;			var bounds:Rectangle = new Rectangle(0, 0, m_segmentation_mask.bitmapData.width, m_segmentation_mask.bitmapData.height);			m_segmentation_mask.bitmapData.fillRect(bounds,0xFFFFFF);			m_segmentation_mask.alpha=0.8;		}				function on_btn_fg(e:MouseEvent) {			m_brush.set_brush_color(fg_color);			m_brush.set_mode(m_brush.MODE_DRAW);						//if(!m_fg_btn.selected) m_fg_btn.selected=true;			m_erase_btn.selected=false;		}		function on_btn_bnd(e:MouseEvent) {			m_brush.set_brush_color(0xFFFF00);			m_brush.set_mode(m_brush.MODE_DRAW);		}		function on_btn_bg(e:MouseEvent) {			m_brush.set_brush_color(0x0000FF);			m_brush.set_mode(m_brush.MODE_DRAW);		}		function on_btn_erase(e:MouseEvent) {			m_brush.set_brush_color(0x000000);			m_brush.set_mode(m_brush.MODE_ERASE);			//if(!m_erase_btn.selected) m_erase_btn.selected=true;			m_fg_btn.selected=false;		}				function reset_zoom_button_Click(e:MouseEvent) {			var button:Button = e.target as Button;			m_sites_holder.width=m_zoom_control.width;			m_sites_holder.height=m_zoom_control.height;			m_sites_holder.x=m_zoom_control.x;			m_sites_holder.y=m_zoom_control.y;				}			   		function zoom_button_Click(e:MouseEvent) {			var button:Button = e.target as Button;			m_zoom_control.visible=!button.selected;		}			function save_segmentation_button_Click(e:MouseEvent) {						var request:URLRequest = new URLRequest(image_base+"datastore/save_segmentation/demo/");				request.method=URLRequestMethod.POST;			var bounds:Rectangle = new Rectangle(0, 0, m_segmentation_mask.bitmapData.width, m_segmentation_mask.bitmapData.height);			var pixels:ByteArray = m_segmentation_mask.bitmapData.getPixels(bounds);			pixels.compress();			var pixels2:ByteArray=new ByteArray();			try{				pixels2.writeByte(86);				pixels2.writeByte(61);			for(var i=0;i<pixels.length;i++){				var b=pixels[i];				pixels2.writeByte(Math.floor(65 + ((b) / 16)));				pixels2.writeByte(Math.floor(65 + ((b) % 16)));			}			}finally{			}				/*			for(var i=0;i<pixels.length;i++){				var b=pixels.readByte();				pixels2.writeByte(48 + b / 16);				pixels2.writeByte(48 + b % 16);			}*/			request.data=pixels2;						var loader:URLLoader = new URLLoader();			loader.addEventListener(Event.COMPLETE,on_save_complete);			loader.load(request);			}					function on_save_complete(e:Event){			var data_ready_evt:Event = new Event("my_all_data_saved");			this.dispatchEvent(data_ready_evt);		}				function load_segmentation_button_Click(e:MouseEvent) {						load_segmentation("/datastore/load_segmentation/demo/");			}				function load_segmentation(url) {						var request:URLRequest = new URLRequest(url);				request.method=URLRequestMethod.POST;			var loader:URLLoader = new URLLoader();			loader.dataFormat=URLLoaderDataFormat.BINARY;			loader.addEventListener(Event.COMPLETE,on_load_complete);			loader.load(request);		}				function on_load_complete(e:Event){			var loader:URLLoader=URLLoader(e.target);			var pixels2:ByteArray=loader.data;			var pixels:ByteArray=new ByteArray();			var header:ByteArray=new ByteArray();						for(var i=0;i<64;i+=2){				var b1=pixels2[i];				var b2=pixels2[i+1];				header.writeByte((b1-65) * 16 + (b2-65) );			}			for(var i=64;i<pixels2.length;i+=2){				var b1=pixels2[i];				var b2=pixels2[i+1];				pixels.writeByte((b1-65) * 16 + (b2-65) );			}			pixels.uncompress();			var bounds:Rectangle = new Rectangle(0, 0, m_segmentation_mask.bitmapData.width, m_segmentation_mask.bitmapData.height);			m_segmentation_mask.bitmapData.setPixels(bounds,pixels);		}				function on_zoom_mouse_down(event:MouseEvent):void		{			trace(event.localX);						if(event.buttonDown){				var scale_step;				if(event.altKey){					scale_step=1/1.4				}else{					scale_step=1.4;				}				var sX=event.stageX;				var sY=event.stageY;				var local_point:Point=m_sites_holder.globalToLocal(new Point(sX,sY));				var zoom_point:Point=m_zoom_control.parent.globalToLocal(new Point(sX,sY));				var parent_point:Point=m_sites_holder.parent.globalToLocal(new Point(sX,sY));								//m_sites_holder.width=m_sites_holder.width;				//m_sites_holder.height=m_sites_holder.height;						m_sites_holder.width=m_sites_holder.width*scale_step;				m_sites_holder.height=m_sites_holder.height*scale_step;										//m_sites_holder.x=m_zoom_control.x+m_zoom_control.width/2-(parent_point.x-local_point.x); //*scale_step;				//m_sites_holder.y=m_zoom_control.y+m_zoom_control.height/2-(parent_point.y-local_point.y);//scale_step; //*scale_step;				//m_sites_holder.x=m_sites_holder.x-2*(m_zoom_control.width/m_sites_holder.width)*zoom_point.x;				//m_sites_holder.y=m_sites_holder.y-2*(m_zoom_control.width/m_sites_holder.width)*zoom_point.y;				//m_sites_holder.x=m_zoom_control.x+m_zoom_control.width/2-(parent_point.x); //*scale_step;				//m_sites_holder.y=m_zoom_control.y+m_zoom_control.height/2-(parent_point.y);//scale_step; //*scale_step;								m_sites_holder.x=m_sites_holder.x-(zoom_point.x-250)*(m_sites_holder.width/500);				m_sites_holder.y=m_sites_holder.y-(zoom_point.y-250)*(m_sites_holder.height/500);//scale_step; //*scale_step;				//m_sites_holder.x=m_zoom_control.x+m_zoom_control.width/2-(parent_point.x+m_sites_holder.width/2); //*scale_step;				//m_sites_holder.y=m_zoom_control.y+m_zoom_control.height/2-(parent_point.y+m_sites_holder.height/2);//scale_step; //*scale_step;			}		}				public function get_xml_annotation():String		{					var object_name=this.label.split('_')[0];			var object_sqn=this.label.split('_')[1];						var xmlStr:String="";						var seg_url= image_base+ "datastore/load_segmentation/"+m_segmentation_id+"/";			var seg_save= image_base+ "datastore/save_segmentation/"+m_segmentation_id+"/";			save_segmentation(seg_save);			xmlStr +='<segmentation name="'+ object_name +'" sqn="'+ object_sqn +'" id="'+m_segmentation_id+'" url="'+seg_url+'" />\n';			return xmlStr;		}				public function set_xml_annotation(segmentation):void		{			var nm=segmentation.@name;			var sqn=segmentation.@sqn;			this.data=nm+"_"+sqn;			this.label=this.data;						m_segmentation_id=segmentation.@id;			var seg_url=segmentation.@url;						load_segmentation(seg_url);		}								function save_segmentation(targetURL:String) {								var request:URLRequest = new URLRequest(targetURL);				request.method=URLRequestMethod.POST;			var bounds:Rectangle = new Rectangle(0, 0, m_segmentation_mask.bitmapData.width, m_segmentation_mask.bitmapData.height);			var header:ByteArray=new ByteArray();						//32 bytes = 8 ints;			header.writeInt(m_segmentation_mask.bitmapData.width)			header.writeInt(m_segmentation_mask.bitmapData.height)			for(var pad=0;pad<6;pad++)				header.writeInt(0);					var pixels:ByteArray = m_segmentation_mask.bitmapData.getPixels(bounds);			pixels.compress();			var pixels2:ByteArray=new ByteArray();			try{				pixels2.writeByte(86);				pixels2.writeByte(61);				for(var i=0;i<header.length;i++){					var b=header[i];					pixels2.writeByte(Math.floor(65 + ((b) / 16)));					pixels2.writeByte(Math.floor(65 + ((b) % 16)));				}				for(var i=0;i<pixels.length;i++){					var b=pixels[i];					pixels2.writeByte(Math.floor(65 + ((b) / 16)));					pixels2.writeByte(Math.floor(65 + ((b) % 16)));				}			}finally{			}			request.data=pixels2;						var loader:URLLoader = new URLLoader();			loader.load(request);	}				function setDisplayMode():void	{		the_image.visible=false;		m_sites_holder.removeEventListener(MouseEvent.MOUSE_MOVE,on_mouse_move);		m_sites_holder.setMode(m_sites_holder.MODE_TRANSPARENT);		this.gotoAndStop(2);	}	function onBtnDoneClick(event:MouseEvent):void	{		//if(this.Mode == IDLE && this.numPts>0)		//{			m_sites_holder.width=m_zoom_control.width;			m_sites_holder.height=m_zoom_control.height;			m_sites_holder.x=m_zoom_control.x;			m_sites_holder.y=m_zoom_control.y;					setDisplayMode();			this.parent.addChildAt(this,2);			var done_event:Event = new Event("my_input_finished");			this.dispatchEvent(done_event);								//pdClickArea.removeEventListener(MouseEvent.MOUSE_OVER, mouseOverHandler);			//pdClickArea.removeEventListener(MouseEvent.MOUSE_OUT, mouseOutHandler);			//pdClickArea.removeEventListener(Event.MOUSE_LEAVE, mouseLeaveHandler);				//}	}	}}