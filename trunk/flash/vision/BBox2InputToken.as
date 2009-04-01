﻿/********************************************************************** Software License Agreement (BSD License)**  Copyright (c) 2008, University of Illinois at Urbana-Champaign*  All rights reserved.**  Redistribution and use in source and binary forms, with or without*  modification, are permitted provided that the following conditions*  are met:**   * Redistributions of source code must retain the above copyright*     notice, this list of conditions and the following disclaimer.*   * Redistributions in binary form must reproduce the above*     copyright notice, this list of conditions and the following*     disclaimer in the documentation and/or other materials provided*     with the distribution.*   * Neither the name of the University of Illinois nor the names of its*     contributors may be used to endorse or promote products derived*     from this software without specific prior written permission.**  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS*  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT*  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS*  FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE*  COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,*  INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,*  BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;*  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER*  CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT*  LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN*  ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE*  POSSIBILITY OF SUCH DAMAGE.*********************************************************************//***** Author: Alexander Sorokin, Department of Computer Science,*                                  University of Illinois at Urbana-Champaign.* Advised by: David Forsyth.*****/package vision{					import flash.display.*;		//import flash.display.Shape;	import fl.controls.Label;	import flash.events.MouseEvent;	import flash.events.Event;	import flash.geom.Rectangle;	import flash.text.*;	 	 dynamic public class BBox2InputToken extends MovieClip	 {		var all_colors:Array=new Array();		var box_points:Array=new Array();		 		 		 //public var m_lbl;		 //var last_object_id;		 var rootObj;		 		 public var min_size:int;		 public var all_controls:Array;		 		 function BBox2InputToken()		 {						all_colors.push(0xFFD700);			all_colors.push(0x0000CC);			all_colors.push(0xFF0000);			all_colors.push(0x00FFD7);			m_input_btn.addEventListener(MouseEvent.CLICK, this.shapeADD);			min_size=-1;						all_controls=new Array();		 }		 public function set_root(newRootObj):void{			 this.rootObj=newRootObj;		 }		 		 function shapeADD(event:Event):void		 {			this.parent.visible=false;			rootObj.last_object_id=rootObj.last_object_id+1;			var newShape:BBox2Input= new BBox2Input();			newShape.lineColor=this.all_colors[rootObj.last_object_id % all_colors.length];			newShape.x=0;//the_sites_holder.x;			newShape.y=0;//the_sites_holder.y;			var shapeLabel=m_input_btn.label+"_"+rootObj.last_object_id.toString();			newShape.label=shapeLabel;			newShape.data=shapeLabel;			newShape.bbox=null;			newShape.min_size=min_size;						rootObj.the_sites_holder.addChild(newShape);			rootObj.shapesListBox.addItem(newShape);			rootObj.all_shapes.push(newShape);			newShape.baseImage=rootObj.the_image;			//makeActive(newShape);			newShape.addEventListener("my_input_finished", onBox_InputFinished);			newShape.detail_object=null;									all_controls.push(newShape);		}				var bX,bY,bW,bH;		function onBox_InputFinished(event:Event):void		{			this.parent.visible=true;			/*			var box_input=event.currentTarget;			box_input.visible=false;						var lx,ly,lw,lh;			lx=box_input.ptsX[1];			ly=box_input.ptsY[1];			lw=box_input.ptsX[2]-lx+1;			lh=box_input.ptsY[2]-ly+1;			bX=lx;			bY=ly;			bW=lw;			bH=lh;			lx=(lx-rootObj.oX)*rootObj.ratio;			ly=(ly-rootObj.oY)*rootObj.ratio;						lw=lw*rootObj.ratio;			lh=lh*rootObj.ratio;						box_input.bbox=[lx,ly,lw,lh];			//box_points.push(new Rectangle(lx,ly, lw,lh));				var thePolygon= new Shape();    			var lbl=box_input.data;			var lineColor=0xFFFF00;			var type=lbl.split("_")[0];			if(type=="ribbon")			{				lineColor=0x0000FF;			}			thePolygon.graphics.lineStyle(2, lineColor, 1, false, LineScaleMode.VERTICAL,											CapsStyle.NONE, JointStyle.MITER, 10);				thePolygon.graphics.moveTo(bX,bY);			thePolygon.graphics.lineTo(bX+bW,bY);			thePolygon.graphics.lineTo(bX+bW,bY+bH);			thePolygon.graphics.lineTo(bX,bY+bH);			thePolygon.graphics.lineTo(bX,bY);			rootObj.the_sites_holder.addChild(thePolygon);						var tag:TextField=new TextField();						tag.text=lbl.split("_")[1];						tag.opaqueBackground=0xFFFFFF;			tag.autoSize=TextFieldAutoSize.RIGHT;			//tag.textField			//tag.y=cY;						rootObj.the_sites_holder.addChild(tag);			tag.x=bX+bW/2-tag.width/2;			tag.y=bY+bH/2-tag.height/2;							//rootObj.all_shapes[all_shapes.length-1].detail_object.visible=false;						rootObj.all_shapes[rootObj.all_shapes.length-1].parent_tag=tag;			rootObj.all_shapes[rootObj.all_shapes.length-1].parent_polygon=thePolygon;			//markDotContainer.visible=true;										/*var bmd2:BitmapData = new BitmapData(lw,lh, false, 0x0000CC44);			var rect:Rectangle = new Rectangle(lx,ly, lw,lh);			var pt:Point = new Point(0,0);			bmd2.copyPixels(rootObj.the_image.bitmapData, rect, pt);			var bm2:Bitmap = new Bitmap(bmd2);			bm2.width=bm2.width/ratio;			bm2.height=bm2.height/ratio;						var detail=new vision.Person14Joints();			detail.addEventListener("my_input_finished", onDetail_InputFinished);			//var newShape= new PersonJointsDisplay();			detail.lineColor=all_colors[all_shapes.length % all_colors.length];			detail.x=0;//the_sites_holder.x;			detail.y=0;//the_sites_holder.y;			detail.label=txtShapeLabel.text;			detail.data=txtShapeLabel.text;			//the_sites_holder.addChild(newShape);			//shapesListBox.addItem(newShape);			//all_shapes.push(newShape);					var t2X=targetX;			var t2Y=targetY;			var oX2,oY2,ratio2;						var rW=bm2.width/t2X;			var rH=bm2.height/t2Y;			ratio2= Math.max(rW,rH);			//txtShapeLabel.text= ratio;			//txtShapeLabel.visible=false;			bm2.width = bm2.width/ratio2;//the_sites_holder.width;			bm2.height = bm2.height/ratio2;//the_sites_holder.height;			oX2=(targetX-bm2.width)/2;			oY2=(targetY-bm2.height)/2;			bm2.x = oX2;			bm2.y = oY2;							detail.inputImageHolder.addChild(bm2);						box_input.detail_object=detail;						the_sites_holder.addChild(detail);			markDotContainer.visible=false;*/			//var label_input;			trace("onInputFinished:"+event.toString())			//shapeADD(undefined);		}				 public function set_name(obj_name:String)		 {			 m_input_btn.label=obj_name;		 }			 public function get_xml_annotation():String		{			var xmlStr:String="";			xmlStr+="<bbox2tk>";			for(var iC=0;iC<all_controls.length;iC++){				xmlStr+=all_controls[iC].get_xml_annotation();							}			xmlStr+="</bbox2tk>";			return xmlStr;		}		 	 } }