﻿/********************************************************************** Software License Agreement (BSD License)**  Copyright (c) 2008, University of Illinois at Urbana-Champaign*  All rights reserved.**  Redistribution and use in source and binary forms, with or without*  modification, are permitted provided that the following conditions*  are met:**   * Redistributions of source code must retain the above copyright*     notice, this list of conditions and the following disclaimer.*   * Redistributions in binary form must reproduce the above*     copyright notice, this list of conditions and the following*     disclaimer in the documentation and/or other materials provided*     with the distribution.*   * Neither the name of the University of Illinois nor the names of its*     contributors may be used to endorse or promote products derived*     from this software without specific prior written permission.**  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS*  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT*  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS*  FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE*  COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,*  INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,*  BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;*  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER*  CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT*  LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN*  ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE*  POSSIBILITY OF SUCH DAMAGE.*********************************************************************//***** Author: Alexander Sorokin, Department of Computer Science,*                                  University of Illinois at Urbana-Champaign.* Advised by: David Forsyth.*****/package vision{	import flash.display.*;	import fl.controls.Label;	import flash.events.MouseEvent;	import flash.events.Event;	import flash.geom.Rectangle;	import flash.text.*;	import vision.PolygonalDisplay;	import vision.InputSpecsControl;	dynamic public class PolygonInputToken extends MovieClip	{		var all_colors:Array=new Array();		var box_points:Array=new Array();		var all_controls:Array;		//public var m_lbl;		//var last_object_id;		var rootObj;		function PolygonInputToken() {			all_colors.push(0xFFD700);			all_colors.push(0x0000CC);			all_colors.push(0xFF0000);			all_colors.push(0x00FFD7);			m_input_btn.addEventListener(MouseEvent.CLICK, this.shapeADD);			all_controls=new Array();		}		public function set_root(newRootObj):void {			this.rootObj=newRootObj;		}		function shapeADD(event:Event):void {			var isc:vision.InputSpecsControl=vision.InputSpecsControl(this.parent);			isc.deactivate();			rootObj.hideSaveBtn();									rootObj.last_object_id=rootObj.last_object_id+1;			var newShape:PolygonalDisplay= new PolygonalDisplay();			newShape.set_root(rootObj);			newShape.lineColor=this.all_colors[rootObj.last_object_id % all_colors.length];			newShape.x=0;			newShape.y=0;			var shapeLabel=m_input_btn.label+"_"+rootObj.last_object_id.toString();			newShape.object_name=m_input_btn.label;			newShape.object_sqn=rootObj.last_object_id;			newShape.set_object_name(newShape.object_name);						newShape.label=shapeLabel;			newShape.data=shapeLabel;			newShape.bbox=null;			rootObj.the_sites_holder.addChild(newShape);			//rootObj.all_shapes.push(newShape);			newShape.baseImage=rootObj.the_image;			newShape.addEventListener("my_input_finished", onBox_InputFinished);			newShape.addEventListener("my_input_cancelled", onBox_InputCancelled);			newShape.detail_object=null;			newShape.setMode(PolygonalDisplay.READY);			newShape.enable_edit();			all_controls.push(newShape);		}		public function enable_edit():void{			for(var iC=0;iC<all_controls.length;iC++){				all_controls[iC].setMode(PolygonalDisplay.EDITING);				all_controls[iC].enable_edit();							} 			m_input_btn.enabled=true;		}				public function enable_edit2():void{			for(var iC=0;iC<all_controls.length;iC++){				//all_controls[iC].setMode(PolygonalDisplay.EDITING);				all_controls[iC].enable_edit2();							} 			m_input_btn.enabled=true;		}		public function disable_edit():void{			for(var iC=0;iC<all_controls.length;iC++){				all_controls[iC].disable_edit();							} 			m_input_btn.enabled=false;		}		var bX,bY,bW,bH;		function onBox_InputFinished(event:Event):void {			var poly_input=event.currentTarget;			poly_input.m_edit_ctrl.visible=false;			//var ptsX:Array;			//var ptsY:Array;			var tag:TextField=new TextField();						var lbl=poly_input.data;						tag.text=lbl.split("_")[0];						tag.opaqueBackground=0xFFFFFF;			tag.autoSize=TextFieldAutoSize.RIGHT;			poly_input.tag=tag;			var lx=poly_input.ptsX[1];			var ly=poly_input.ptsY[1];						rootObj.the_sites_holder.addChild(tag);			tag.x=lx-tag.width/2;			tag.y=ly-tag.height/2;			//rootObj.the_sites_holder.addChild(poly_input.thePolygon);			//rootObj.the_sites_holder.removeChild(poly_input);						//rootObj.all_shapes[all_shapes.length-1].detail_object.visible=false;						//rootObj.all_shapes[rootObj.all_shapes.length-1].parent_tag=tag;			//rootObj.all_shapes[rootObj.all_shapes.length-1].parent_polygon=null;						poly_input.enable_edit2();			poly_input.setMode(PolygonalDisplay.SELECTION);			rootObj.the_sites_holder.addChild(poly_input.thePolygon);			poly_input.visible=false;						trace("onInputFinished:"+event.toString());			//shapeADD(undefined); 			var isc:vision.InputSpecsControl=vision.InputSpecsControl(this.parent);			isc.activate();			rootObj.showSaveBtn();		}		function onBox_InputCancelled(event:Event):void {			var poly_input=event.currentTarget;			//poly_input.m_cover.visible=false;						rootObj.the_sites_holder.removeChild(poly_input);			this.all_controls.pop()			var isc:vision.InputSpecsControl=vision.InputSpecsControl(this.parent);			isc.activate();			rootObj.showSaveBtn();											}				public function set_name(obj_name:String) {			m_input_btn.label=obj_name;		}		public function add_xml_annotation(obj:XML):void		{			var newShape:PolygonalDisplay= new PolygonalDisplay();			newShape.set_root(rootObj);			newShape.read_xml_annotation(obj);			newShape.setMode(PolygonalDisplay.DISPLAY);			rootObj.the_sites_holder.addChild(newShape);			all_controls.push(newShape);		}		 public function get_xml_annotation():String		{			var xmlStr:String="";			//xmlStr+="<polyTK>";			//xmlStr+="<polyTK name='"+ m_input_btn.label +"'>";				for(var iC=0;iC<all_controls.length;iC++){				xmlStr+=all_controls[iC].get_xml_annotation();							}			//xmlStr+="</polyTK>";			return xmlStr;		}		 			}}