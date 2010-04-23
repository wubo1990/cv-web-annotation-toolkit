
function stop_bubble(event)
{
    if (!e) var e = window.event;
    e.cancelBubble = true;
    if (e.stopPropagation) e.stopPropagation();
}

var table_cell_click=function(event)
{
    element=Event.element(event) 
    inp=element.select("input");
    if (inp.length==0)
	return;

    for( var i =0; i<inp.length;i++)
    {
	f=inp[i];
	if(f.type=="checkbox")
	    {			
		f.checked=1-f.checked;
	    }
	else if(f.type=="select-one"){
	    //pass
	}else if(f.type=="textarea"){
	    //pass
	}else if(f.type=="radio"){
	    f.checked=true;
	}else if(f.type=="text"){
	    f.focus();
	    //pass;
	}else{
	    for( var fID=0;fID<f.length;fID++)
		{
		    var field=f[fID];
		    if(field.value==attr_val)
			{
			    field.checked=true;
			    break;
			}
		}
	}
    }
    if(click_once)
	{
	    go_next();
	}
}


var set_attribute_value=function(obj_id,attr_name,attr_val)
{

    f=$('MT_form')['A_obj'+obj_id+'_'+attr_name];
    if(f.type=="checkbox")
	{			
	    if(attr_val=="on")
		f.checked=1;
	}
    else if(f.type=="select-one"){
	f. value=attr_val;
    }else if(f.type=="textarea"){
	f.value=attr_val;
    }else{
	for( var fID=0;fID<f.length;fID++)
	    {
		var field=f[fID];
		if(field.value==attr_val)
		    {
			field.checked=true;
			break;
		    }
	    }
    }
};


var get_attribute_names=function(parameters_data)
{
    var attributes_root = parameters_data.getElementsByTagName('attributes')[0];
    var attributes=attributes_root.getElementsByTagName('attribute');  
    var attribute_names=[];			  
    for( var aID=0;aID<attributes.length;aID++)
	{
            var attr_id=attributes[aID].getAttribute('id');
	    attribute_names[aID]= attr_id ;
	}
    return attribute_names;
}

var set_submission_data=function(attribute_names,annotation_data)
{

	  var objects=annotation_data.getElementsByTagName('object');
			       
          for( var oID=0;oID<objects.length;oID++)
          {
	     var object=objects[oID];
	     var obj_id = object.getAttribute('id');
             for( var aID=0;aID<attribute_names.length;aID++)
             {
		var attr=object.getAttribute(attribute_names[aID]);

		if(attr==null)
		{
		}else{
		    set_attribute_value(obj_id,attribute_names[aID],attr);
		}
             }
          }
	  var comments=annotation_data.getElementsByTagName('comments');
	  var comments_str="";
	  for(var iC=0;iC<comments.length;iC++)
	  { 
	    comments_str += comments[iC].getAttribute('text');
	  }
          $('Comments').value=comments_str;
};


var set_initial_attribute_values=function(attribute_names,task_data)
{
    var items=task_data.getElementsByTagName('item');

    for( var iID=0;iID<items.length;iID++)
	{
	    var i=items[iID];
	    var obj_id = i.getAttribute("id");
	    var attributes=i.getElementsByTagName('attributes');
	    if( attributes.length>0)
		{
		    var attrs=attributes[0];
		    for( var aID=0;aID<attribute_names.length;aID++)
			{
			    
			    var attr=attrs.getAttribute(attribute_names[aID]);
			    if(attr==null)
				{
				}else{
				set_attribute_value(obj_id,attribute_names[aID],attr);
			    }
			}
		}
	}
    
};



var go_next=function()
{
    if(preview_mode_only)
    {
	alert('Please accept the HIT before doing any work');
	return;
    }
    $("task_"+get_id(current_position)).hide();
    current_position = current_position + 1; 
    if(current_position<num_items)
    {
	$("task_"+get_id(current_position)).show();
    }

    if(current_position>=num_items-1){
	if(preview_mode_only){
	}else{
	    document.getElementById('submitButton').disabled = false;
	}
    }
}