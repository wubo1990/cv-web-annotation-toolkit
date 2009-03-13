﻿/********************************************************************** Software License Agreement (BSD License)**  Copyright (c) 2008, University of Illinois at Urbana-Champaign*  All rights reserved.**  Redistribution and use in source and binary forms, with or without*  modification, are permitted provided that the following conditions*  are met:**   * Redistributions of source code must retain the above copyright*     notice, this list of conditions and the following disclaimer.*   * Redistributions in binary form must reproduce the above*     copyright notice, this list of conditions and the following*     disclaimer in the documentation and/or other materials provided*     with the distribution.*   * Neither the name of the University of Illinois nor the names of its*     contributors may be used to endorse or promote products derived*     from this software without specific prior written permission.**  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS*  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT*  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS*  FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE*  COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,*  INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,*  BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;*  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER*  CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT*  LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN*  ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE*  POSSIBILITY OF SUCH DAMAGE.*********************************************************************//***** Author: Alexander Sorokin, Department of Computer Science,*                                  University of Illinois at Urbana-Champaign.* Advised by: David Forsyth.*****/package vision{			import flash.display.*;		//import flash.display.Shape;	import fl.controls.Label;	import flash.events.MouseEvent;	import flash.events.KeyboardEvent;	import flash.events.Event;	import flash.ui.Mouse;		import flash.geom.Point;	import vision.Box2Marker;	import vision.MarkCursor;	import flash.text.*;	 	 dynamic public class BBox2Input extends MovieClip	 {		public const IDLE:String = "idle";		public const EDITING_BOX:String = "edit_box";		public const READY:String = "ready";				public const DISPLAY:String = "display";		public var boxes:Array;				public var ptsX:Array;		public var ptsY:Array;		public var ptsTime:Array;		public var tokens:Array;		public var keys:Array;		public var clickTimes:Array;		public var numPts:Number;		public var thePolygon:Shape;		public var str_joint_names:String = new String("hood-left,hood-right,trunk-right,trunk-left");		public var joint_names:Array = str_joint_names.split(",");		public  var joint_links:Array=new Array();		public var detail_object=null;		public var parent_display=null;		public var parent_tag=null;		public var parent_polygon=null;		public var theBox=null;				public var hitTime:Number;		public var now:Date = new Date();				public var makeActive;				public var lineColor;		public var bbox;				public var m_current_marker:vision.Box2Marker;		public var Mode=IDLE;				public var min_size:int;				//public var m_mark_cursor:vision.MarkCursor;		function BBox2Input(){			joint_links[1]=[];			joint_links[2]=[1];			joint_links[3]=[2];			joint_links[4]=[3,1];			hitTime=now.getTime();			btnRemoveLast.visible=false;			btnDone.visible=false;			theGuide.gotoAndStop(1);			theGuide.visible=true;			//pdClickArea.addEventListener(MouseEvent.CLICK, handleRegularClick);			btnRemoveLast.addEventListener(MouseEvent.CLICK, onRemoveLastSegmentClick);			btnDone.addEventListener(MouseEvent.CLICK, onBtnDoneClick);			pdClickArea.addEventListener(MouseEvent.MOUSE_DOWN, startBox);			pdClickArea.addEventListener(MouseEvent.MOUSE_UP, endBox);			pdClickArea.addEventListener(MouseEvent.MOUSE_MOVE, updateBox);			pdClickArea.addEventListener(MouseEvent.CLICK, killClickEvent);			//m_current_marker.addEventListener(MouseEvent.MOUSE_UP, endBox);			//m_current_marker.addEventListener(MouseEvent.MOUSE_MOVE, updateBox);						numPts=0;			ptsX=new Array();			ptsY=new Array();			ptsTime=new Array();			boxes=new Array();			//m_mark_cursor//= new vision.MarkCursor();						pdClickArea.addEventListener(MouseEvent.MOUSE_OVER, mouseOverHandler);            pdClickArea.addEventListener(MouseEvent.MOUSE_OUT, mouseOutHandler);            //cursor = new CustomCursor();            //addChild(cursor);			m_mark_cursor.visible=false;            pdClickArea.addEventListener(Event.MOUSE_LEAVE, mouseLeaveHandler);			pdClickArea.addEventListener(KeyboardEvent.KEY_DOWN, onKeyDownHandler);			min_size=-1;		}		private function onKeyDownHandler(event:KeyboardEvent):void{			if(event.keyCode == 13){				onBtnDoneClick(null);			}		}				        private function mouseOverHandler(event:MouseEvent):void {            trace("mouseOverHandler");            Mouse.hide();			m_mark_cursor.visible=true;            pdClickArea.addEventListener(MouseEvent.MOUSE_MOVE, mouseMoveHandler);        }        private function mouseOutHandler(event:MouseEvent):void {            trace("mouseOutHandler");            Mouse.show();			m_mark_cursor.visible=false;            pdClickArea.removeEventListener(MouseEvent.MOUSE_MOVE, mouseMoveHandler);            //cursor.visible = false;        }		private function mouseLeaveHandler(event:Event):void {            trace("mouseLeaveHandler");            mouseOutHandler(new MouseEvent(MouseEvent.MOUSE_MOVE));        }		private function mouseMoveHandler(event:MouseEvent):void {            trace("mouseMoveHandler");			var p2:Point=pdClickArea.globalToLocal(new Point(event.stageX,event.stageY));            m_mark_cursor.x = p2.x;            m_mark_cursor.y = p2.y;            event.updateAfterEvent();            m_mark_cursor.visible = true;        }				public function get_xml_annotation():String		{					var object_name=this.label.split('_')[0];			var object_sqn=this.label.split('_')[1];						var iBox=Math.floor((this.numPts+1)/2);			var xmlStr:String="";			xmlStr +='<bbox2 name="'+ object_name +'" sqn="'+ object_sqn +'" >\n';					for(var iB=1;iB<=iBox;iB++){				var iPt1=iB*2-1;				var bx=ptsX[iPt1];				var by=ptsY[iPt1];				var bw=ptsX[iPt1+1]-bx;				var bh=ptsY[iPt1+1]-by;								xmlStr +='<bbox name="'+ object_name +'" sqn="'+ iB +'" left="'+ bx +'" top="'+ by +'" width="'+ bw +'" height="'+ bh +'">\n';				for(var iPt=iB*2-1;iPt<=iB*2;iPt++){				 	var lx=ptsX[iPt];					var ly=ptsY[iPt];					var t =ptsTime[iPt];										xmlStr +='\t<pt x="'+lx+'" y="'+ly+'" ct="'+t+'"/>\n';				}		 				xmlStr += '</bbox>\n';			}			xmlStr += '</bbox2>\n';			return xmlStr;		}				public function set_xml_annotation(bboxes):void		{			var nm=bboxes.@name;			var sqn=bboxes.@sqn;			this.data=nm+"_"+sqn;						for each(var o in bboxes.bbox){				//var bboxInput:BBoxInput=new BBoxInput();				//bboxInput.setXML(o);				//<bbox name="lamp" sqn="1" left="334.89000000000004" top="27.067500000000003" width="23.625" height="20.11500000000001"/>							var lx,ly,lw,lh,bX,bY,bW,bH;				lx=o.@left;				ly=o.@top;				lw=o.@width;				lh=o.@height;								m_current_marker=new vision.Box2Marker();				m_current_marker.x=lx;				m_current_marker.y=ly;				m_current_marker.width=lw;				m_current_marker.height=lh;								if ((lw<=1) || (lh<=1)){					m_current_marker.highlight_invalid();				}else{					m_current_marker.gotoAndStop(2);				}				this.addChild(m_current_marker);												var tag:TextField=new TextField();								tag.text=sqn+"/"+o.@sqn+" "+o.@name;								tag.background=false;				tag.autoSize=TextFieldAutoSize.RIGHT;								this.addChild(tag);				tag.x=Number(lx);//+bW/2-tag.width/2;				tag.y=Number(ly)+tag.height/2;//bY+bH/2-tag.height/2;										tag=new TextField();								tag.text=sqn+"/"+o.@sqn+" "+o.@name;								tag.background=false;				tag.autoSize=TextFieldAutoSize.RIGHT;								this.addChild(tag);				tag.x=Number(lx)+2;//+bW/2-tag.width/2;				tag.y=Number(ly)+tag.height/2+2;//bY+bH/2-tag.height/2;									tag.textColor=0xFFFFFF;						}		}		function onFinishShapeClick(event:MouseEvent):void		{			var now:Date = new Date();			this.hitTime=now.getTime();			thePolygon.graphics.lineTo(ptsX[1], ptsY[1]);			this.Mode=IDLE;			btnRemoveLast.visible=false;			theGuide.visible=false;						pdClickArea.removeEventListener(MouseEvent.MOUSE_OVER, mouseOverHandler);            pdClickArea.removeEventListener(MouseEvent.MOUSE_OUT, mouseOutHandler);            pdClickArea.removeEventListener(Event.MOUSE_LEAVE, mouseLeaveHandler);		}//btnFinishShape.addEventListener(MouseEvent.CLICK, onFinishShapeClick);									function startBox(event:MouseEvent):void {//			ptsX[1]=event.target.startDrag(true);			if(this.Mode == this.IDLE){			numPts++;			var p2:Point=pdClickArea.globalToLocal(new Point(event.stageX,event.stageY));			ptsX[numPts]=p2.x;			ptsY[numPts]=p2.y;			var now:Date;			now = new Date();			ptsTime[numPts]=now.getTime();			m_current_marker=new vision.Box2Marker();			m_current_marker.x=ptsX[numPts];			m_current_marker.y=ptsY[numPts];			m_current_marker.addEventListener(MouseEvent.MOUSE_UP, endBox);			m_current_marker.addEventListener(MouseEvent.MOUSE_MOVE, updateBox);			m_current_marker.width=0;			m_current_marker.height=0;			pdClickArea.addChild(m_current_marker);			boxes[(numPts+1)/2]=m_current_marker;			//event.stopPropagation();			this.Mode = this.EDITING_BOX			}		}		function endBox(event:MouseEvent):void {			if(	this.Mode == this.EDITING_BOX){				var p2:Point=pdClickArea.globalToLocal(new Point(event.stageX,event.stageY));				var w=p2.x-m_current_marker.x;				var h=p2.y-m_current_marker.y;								if ( (w<=0) || (h<=0) ){					numPts--;				}else{					numPts++;									ptsX[numPts]=p2.x;					ptsY[numPts]=p2.y;					var now:Date;					now = new Date();					ptsTime[numPts]=now.getTime();				}				//event.stopPropagation();				this.Mode = this.IDLE;				btnDone.visible=true;			}		}		function updateBox(event:MouseEvent):void {			if(	this.Mode == this.EDITING_BOX){				var x1=ptsX[numPts];				var y1=ptsY[numPts];				var x2=event.stageX;				var y2=event.stageY;				//trace(x2,y2);				var p2:Point=pdClickArea.globalToLocal(new Point(x2,y2));				var w=p2.x-m_current_marker.x;				var h=p2.y-m_current_marker.y;								m_current_marker.width=Math.max(0,p2.x-m_current_marker.x);				m_current_marker.height=Math.max(0,p2.y-m_current_marker.y);				if ( (w<=0) || (h<=0) ){					w=0;h=0;				}else{					if(min_size>0){						w=Math.max(min_size,w);						h=Math.max(min_size,h);					}else{						w=Math.max(0,w);						h=Math.max(0,h);					}				}				m_current_marker.width=w;				m_current_marker.height=h;			}			//event.stopPropagation();		}				function killClickEvent(event:MouseEvent):void {			//event.stopPropagation();		}	function handleRegularClick(event:MouseEvent):void{	var links;	var n;	var i;	var now:Date;	var key=0;	var mark;		if(event.altKey)	{		key=1;	}		if(this.Mode==IDLE){		trace("Idle")	}else if(this.Mode==READY){		//btnFinishShape.x=event.localX;		//btnFinishShape.y=event.localY;		//btnFinishShape.visible=true;		btnRemoveLast.visible=true;		theGuide.visible=true;		//lblRemoveLast.visible=true;		this.Mode=EDITING_BOX;				ptsX=new Array();		ptsY=new Array();		ptsTime=new Array();		tokens=new Array();		keys=new Array();		numPts=0;   		thePolygon= new Shape();            thePolygon.graphics.lineStyle(2, lineColor, 1, false, LineScaleMode.VERTICAL,                               CapsStyle.NONE, JointStyle.MITER, 10);		numPts++;		ptsX[numPts]=event.localX;		ptsY[numPts]=event.localY;		now = new Date();		ptsTime[numPts]=now.getTime();		keys[numPts]=key;		theGuide.gotoAndStop(numPts*5+1);				mark=new MarkSymbol();		tokens[numPts]=mark;				mark.x=event.localX;		mark.y=event.localY;		pdClickArea.addChild(mark);			 			}else if(this.Mode==EDITING_BOX){				if(numPts<2)		{			if(event.localX>=ptsX[numPts] && event.localY>=ptsY[numPts] &&				! (event.localX==ptsX[numPts] && event.localY==ptsY[numPts]))			{			numPts++;			ptsX[numPts]=event.localX;			ptsY[numPts]=event.localY;			now = new Date();			ptsTime[numPts]=now.getTime();			keys[numPts]=key;							//theGuide.gotoAndStop(numPts*5+1);	 	//thePolygon.graphics.lineTo(event.localX, event.localY);			//mark2=new MarkSymbol();			//tokens[numPts]=mark2;			//mark2.x=event.localX;			//mark2.y=event.localY;						theBox=new Shape();			lineColor=0xFFFFFF;        	theBox.graphics.lineStyle(2, lineColor, 1, false, LineScaleMode.VERTICAL,                               CapsStyle.NONE, JointStyle.MITER, 10);			var bX=ptsX[1];			var bY=ptsY[1];			var bW=ptsX[2]-bX+1;			var bH=ptsY[2]-bY+1;			theBox.graphics.moveTo(bX,bY);			theBox.graphics.lineTo(bX+bW,bY);			theBox.graphics.lineTo(bX+bW,bY+bH);			theBox.graphics.lineTo(bX,bY+bH);			theBox.graphics.lineTo(bX,bY);			tokens[numPts]=theBox;			//the_sites_holder.addChild(thePolygon);			pdClickArea.addChild(theBox);			btnDone.visible=true;			}					////		 if(numPts==2){//			 var cX=0;//			 var cY=0;//			 for(var ii:Number=1;ii<=numPts;ii++)//			 {//				cX=cX+ptsX[ii];//				cY=cY+ptsY[ii];	//			 }//			 cX=cX/numPts;//			 cY=cY/numPts;////			 var tag:TextField=new TextField();//			 tag.text=this.data.substr(4);//			 tag.opaqueBackground=0xFFFFFF;//			 tag.autoSize=TextFieldAutoSize.RIGHT;//			 //tag.textField//			 //tag.y=cY;//			 //			 this.addChild(tag);//			 tag.x=cX-tag.width/2;//			 tag.y=cY-tag.height/2;//			 this.Mode=IDLE;//			//btnFinishShape.visible=false;//			btnRemoveLast.visible=false;//			theGuide.visible=false;//			//			var done_event:Event = new Event("my_input_finished");//        	this.dispatchEvent(done_event);//		 }		}		trace(event.currentTarget.toString() + 			" dispatches MouseEvent. Local coords [" + 			event.localX + "," + event.localY + "] Stage coords [" + 			event.stageX + "," + event.stageY + "]");	}	trace(event.currentTarget.toString() + 			" dispatches MouseEvent. Local coords [" + 			event.localX + "," + event.localY + "] Stage coords [" + 			event.stageX + "," + event.stageY + "]");	now = new Date();	this.hitTime=now.getTime();}////var mouse_localX=0;//var mouse_localY=0;//pdClickArea.addEventListener(MouseEvent.MOUSE_MOVE, mouseTracker);//function mouseTracker(event:MouseEvent):void//{//	mouse_localX=event.localX;//	mouse_localY=event.localY;//	//}////pdClickArea.addEventListener(KeyboardEvent.KEY_UP, handleKeyboard);////function handleKeyboard(event:KeyboardEvent):void//{//	var links;//	var n;//	var i;//	var now:Date;//	var key=event.charCode;//	trace(key);//	if(key=='s' || key=='g'){//	if(this.Mode==IDLE){//		trace("Idle")//	}else if(this.Mode==READY){//		//btnFinishShape.x=event.localX;//		//btnFinishShape.y=event.localY;//		//btnFinishShape.visible=true;//		btnRemoveLast.visible=true;//		theGude.visible=true;//		//lblRemoveLast.visible=true;//		this.Mode=EDITING;//		//		ptsX=new Array();//		ptsY=new Array();//		clickTimes=new Array();//		numPts=0;//   		thePolygon= new Shape();    ////        thePolygon.graphics.lineStyle(2, lineColor, 1, false, LineScaleMode.VERTICAL,//                               CapsStyle.NONE, JointStyle.MITER, 10);////		numPts++;//		ptsX[numPts]=mouse_localX;//		ptsY[numPts]=mouse_localY;//		theGude.gotoAndStop(numPts*5+1);//		now = new Date();//		clickTimes[numPts]=now.getTime();//		// 		 thePolygon.graphics.moveTo(mouse_localX, mouse_localY);//		 links=joint_links[numPts];//		 for(i=0;i<links.length;i++)//		 {//			n=links[i];//			thePolygon.graphics.lineTo(ptsX[n], ptsY[n]);//		 }//		 event.currentTarget.addChild(thePolygon);// 		//	}else{		//		if(numPts<14)//		{//		numPts++;//		ptsX[numPts]=mouse_localX;//		ptsY[numPts]=mouse_localY;//		now = new Date();//		clickTimes[numPts]=now.getTime();//		//		theGude.gotoAndStop(numPts*5+1);//	 	//thePolygon.graphics.lineTo(event.localX, event.localY);//// 		 thePolygon.graphics.moveTo(mouse_localX, mouse_localY);//		 links=joint_links[numPts];//		 for(i=0;i<links.length;i++)//		 {//			 n=links[i];//			trace(n);// 		 	thePolygon.graphics.moveTo(ptsX[numPts], ptsY[numPts]);//			thePolygon.graphics.lineTo(ptsX[n], ptsY[n]);////		 }		//		 if(numPts==14){//			this.Mode=IDLE;//			//btnFinishShape.visible=false;//			btnRemoveLast.visible=false;//			theGude.visible=false;//		 }//		}//		//trace(event.currentTarget.toString() + ////			" dispatches MouseEvent. Local coords [" + ////			event.localX + "," + event.localY + "] Stage coords [" + ////			event.stageX + "," + event.stageY + "]");//	}////	trace(event.currentTarget.toString() + ////			" dispatches MouseEvent. Local coords [" + ////			event.localX + "," + event.localY + "] Stage coords [" + ////			event.stageX + "," + event.stageY + "]");//	now = new Date();//	this.hitTime=now.getTime();//	}//}function onRemoveLastSegmentClick(event:MouseEvent):void{	if(this.Mode == EDITING_BOX || this.Mode == IDLE)	{		var now:Date = new Date();		this.hitTime=now.getTime();			if(this.numPts>0)		{			var iBox=Math.floor((this.numPts+1)/2);						this.pdClickArea.removeChild(boxes[iBox]);			this.numPts=(iBox-1)*2;			this.Mode=IDLE;		}			if(this.numPts==0){			btnDone.visible=false;		}	}}function setDisplayMode():void{	this.Mode = DISPLAY;	var iBox=Math.floor((this.numPts+1)/2);	var lbl=this.data;	for(var i=1;i<=iBox;i++){		boxes[i].gotoAndStop(2);		var tag:TextField=new TextField();			tag.text=lbl.split("_")[1];		if(iBox>1)		{			tag.text=tag.text+"/"+i;		}		tag.opaqueBackground=0xFFFFFF;		tag.autoSize=TextFieldAutoSize.RIGHT;			this.pdClickArea.addChild(tag);		tag.x=boxes[i].x;//-tag.width/2;		tag.y=boxes[i].y+tag.height/2;			}	this.gotoAndStop(2);	}			function onBtnDoneClick(event:MouseEvent):void{	if(this.Mode == IDLE && this.numPts>0)	{		setDisplayMode();		var done_event:Event = new Event("my_input_finished");    	this.dispatchEvent(done_event);						pdClickArea.removeEventListener(MouseEvent.MOUSE_OVER, mouseOverHandler);		pdClickArea.removeEventListener(MouseEvent.MOUSE_OUT, mouseOutHandler);		pdClickArea.removeEventListener(Event.MOUSE_LEAVE, mouseLeaveHandler);	}}	} } 