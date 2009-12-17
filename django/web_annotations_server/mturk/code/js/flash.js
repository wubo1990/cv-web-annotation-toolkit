AC_FL_RunContent = 0;


var create_flash_video=function(id,src,w,h,play)
{
	swf='video_display';
	swf_w=w;
	swf_h=h;
	query_args='video_url='+src;
	if(play=="play"){
		 query_args+="&video_mode=play";
        }

	return AC_FL_RunContent2(
		 'codebase', 'http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=9,0,0,0',
		 'width', swf_w,
		 'height', swf_h,
		 'src', swf,
		 'quality', 'high',
		 'pluginspage', 'http://www.macromedia.com/go/getflashplayer',
		 'align', 'middle',
		 'play', 'true"',
		 'loop', 'true',
		 'scale', 'showall',
		 'wmode', 'window',
		 'devicefont', 'false',
		 'id', 'annotation_gui',
		 'bgcolor', '#ffffff',
		 'name', 'annotation_gui',
		 'menu', 'true',
		 'allowFullScreen', 'false',
		 'allowScriptAccess','always',
		 'movie', swf,
		 'salign', '',
		 'FlashVars', query_args
	 ); //end AC code
 }




