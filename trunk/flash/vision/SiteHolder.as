﻿/********************************************************************** Software License Agreement (BSD License)**  Copyright (c) 2008, University of Illinois at Urbana-Champaign*  All rights reserved.**  Redistribution and use in source and binary forms, with or without*  modification, are permitted provided that the following conditions*  are met:**   * Redistributions of source code must retain the above copyright*     notice, this list of conditions and the following disclaimer.*   * Redistributions in binary form must reproduce the above*     copyright notice, this list of conditions and the following*     disclaimer in the documentation and/or other materials provided*     with the distribution.*   * Neither the name of the University of Illinois nor the names of its*     contributors may be used to endorse or promote products derived*     from this software without specific prior written permission.**  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS*  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT*  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS*  FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE*  COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,*  INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,*  BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;*  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER*  CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT*  LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN*  ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE*  POSSIBILITY OF SUCH DAMAGE.*********************************************************************//***** Author: Alexander Sorokin, Department of Computer Science,*                                  University of Illinois at Urbana-Champaign.* Advised by: David Forsyth.*****/package vision{			import flash.display.*;	 	 dynamic public class SiteHolder extends MovieClip	 {		public const MODE_OPAQUE:String = "opaque";		public const MODE_TRANSPARENT:String = "transparent";		var Mode:String;		var background_image_reference;		function SiteHolder(){			background_image_reference=null;		}				public function getBG():Object{			return background_image_reference;		}		public function setBG(bg:Object):void{			background_image_reference=bg;		}				public function setMode(new_mode:String):void		{			Mode = new_mode;			if (Mode==MODE_TRANSPARENT){				if (background_image_reference!=null){					background_image_reference.visible=false;				}				gotoAndStop(2);			}else{				gotoAndStop(1);			}					}		static function sortOnVisibility(a:Array, b:Array):Number {   		var aV:Number=a[0];		var bV:Number=b[0]; 		if(aV > bV) {        	return 1;    	} else if(aV < bV) {        	return -1;   		} else  {        	//aPrice == bPrice        	return 0;    	}		}		public function orderElementsByVisibility():void{			var child:DisplayObject;			var visible_elements:Array=new Array();    		for (var i:int=0; i < this.numChildren; i++)    		{        		child = this.getChildAt(i);        		trace("\t", child, child.name); 				if(child is AnnotationElement){					var ae=AnnotationElement(child);					var v=ae.getVisibility();					visible_elements.push([v,child]);        			trace("\t", v); 				}		    }			if(	visible_elements.length>0){				var insertion_offset=this.numChildren-visible_elements.length;				visible_elements.sort(sortOnVisibility,Array.DESCENDING);    			for (var i:int=visible_elements.length-1;i>=0; i--){					var visibility_pair:Array=visible_elements[i];					this.addChildAt(visibility_pair[1],i+insertion_offset);				}			}		}	}	 } 