var create_flash_interface=function(swf,swf_w,swf_h,query_args){
  if (AC_FL_RunContent == 0) {
    alert("This page requires AC_RunActiveContent.js.");
  } else {
    $('flash_div').innerHTML=
      AC_FL_RunContent2(
	'codebase', 'http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=9,0,0,0',
	'width', swf_w,
	'height', swf_h,
	'src', swf,
	'quality', 'high',
	'pluginspage', 'http://www.macromedia.com/go/getflashplayer',
	'align', 'middle',
	'play', 'true',
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
}

var create_video_flash=function(id,src,w,h,play)
{
    swf='/code/video_display';
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



var scale_flash_ui=function(flash_id,scale)
{
    $(flash_id).width=swf_w * scale;
    $(flash_id).height=swf_h * scale;
    persistent_ui_scale = scale;
    set_persistent_value('ui_scale',scale);
}