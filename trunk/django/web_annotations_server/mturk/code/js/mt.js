//
// This method Gets URL Parameters (GUP)
//
var gup=function( name )
{
  var regexS = "[\\?&]"+name+"=([^&#]*)";
  var regex = new RegExp( regexS );
  var tmpURL = window.location.href;
  var results = regex.exec( tmpURL );
  if( results == null )
    return "";
  else
    return results[1];
}

//
// This method decodes the query parameters that were URL-encoded
//
var decode= function (strToDecode)
{
  var encoded = strToDecode;
  return unescape(encoded.replace(/\+/g,  " "));
}


var MT_setup = function (){

    document.getElementById('assignmentId').value = gup('assignmentId');
    //
    // Check if the worker is PREVIEWING the HIT or if they've ACCEPTED the HIT
    //
    if (gup('assignmentId') == "ASSIGNMENT_ID_NOT_AVAILABLE")
    {
        // If we're previewing, disable the button and give it a helpful message
	document.getElementById('submitButton').disabled = true;
	document.getElementById('submitButton').value = "You must ACCEPT the HIT before you can submit the results.";
    } else {
        var form = document.getElementById('MT_form');
        if (document.referrer && ( document.referrer.indexOf('workersandbox') != -1) ) {
            form.action = "http://workersandbox.mturk.com/mturk/externalSubmit";
        }
    }
}


var MT_setup_instructions=function()
{
  instructions_URL=unescape(gup("instructions"));
  $('a_instructions').href=instructions_URL;
}

function create_flash_interface(swf,swf_w,swf_h,query_args){
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


var mt_mode;

var active_task_data;
var annotation_data;
var parameters_data;
var data_done=0;
var annotation_done=0;
var parameters_done=0;

var all_loaded_handler;

var mt_after_load = function()
{

  if(mt_mode=="input")
    {
      if(data_done && parameters_done)
      {
	all_loaded_handler();
      }
    }
  else if(mt_mode=="display")
    {
      if(data_done && parameters_done && annotation_done)
	{
	  all_loaded_handler();
	}

    }
}


var mt_onTaskXMLLoaded=function(transport)
{

  if (transport.responseXML)
  {
    active_task_data = transport.responseXML;
    data_done=1;
    mt_after_load();
   }
}


var mt_onAnnotationXMLLoaded=function(transport)
{
  if (transport.responseXML)
  {
    annotation_data = transport.responseXML;
    annotation_done=1;
    mt_after_load();

  }
}

var mt_onParametersXMLLoaded=function(transport)
{
  if (transport.responseXML)
  {
    parameters_data = transport.responseXML;
    parameters_done=1;
    mt_after_load();

  }
}


var mt_get_param=function (parameters_xml,parameter_name,default_value)
{
  var param_nodes=parameters_xml.getElementsByTagName(parameter_name);
  if(param_nodes.length>0)
  {
    return param_nodes[0].textContent;
  }else{
    return default_value;
  }

};



var mt_load_task_componentes =function(mode,completion_handler)
{
  all_loaded_handler=completion_handler;
  mt_mode=mode;
  parameters_url=decode(gup("parameters_url"));
  if(parameters_url!="")
    {
      var upd=new Ajax.Request(parameters_url, {
				 method: 'get',
				 onSuccess: mt_onParametersXMLLoaded
			       });
    }

  if(mode=="input")
  {

    data_url=decode(gup("data_url"));
    var upd=new Ajax.Request(data_url, {
			       method: 'get',
			       onSuccess: mt_onTaskXMLLoaded
			       });

  }
  else if(mode=="display")
  {
    data_url=unescape(gup("data_url"));
    var upd=new Ajax.Request(data_url, {
			       method: 'get',
			       onSuccess: mt_onTaskXMLLoaded
			     });


    annotation_URL=unescape(gup("annotation_url"));
    var upd=new Ajax.Request(annotation_URL, {
			       method: 'get',
			       onSuccess: mt_onAnnotationXMLLoaded
			     });
  }


}


var mt_submit_handler=function (){
  var now=new Date();
  $('submit_time').value=now.toUTCString();
  return true;
}