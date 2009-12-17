var show_txt=function(txt){
    return txt.replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/\n/g,"<br/>").replace(/ /g,"&nbsp;");
}
var any__all_loaded_handler = function()
{
    if(verbosity>5)
	{
	    $('verbose_parameters').style.display='block';
	    if(mt_mode=="input")
		{
		    $('parameters').innerHTML=show_txt(parameters_resp.responseText);
		    $('work_unit').update(show_txt(active_task_resp.responseText));
		    
		}
	    else
		{
		    $('parameters').innerHTML=show_txt(parameters_resp.responseText);
		    $('work_unit').innerHTML=show_txt(active_task_resp.responseText);
		    $('submission').innerHTML=show_txt(annotation_resp.responseText);
		}
	}
    else
	{

	}
    var images=active_task_data.getElementsByTagName('img');
    for(var i=0;i<images.length;i++)
	{
	    t="A_"+images[i].getAttribute('tgt');
	    $(t).src=images[i].getAttribute('src');
	}
    $('task_content').style.display="block";	    
    $('task_loading').style.display="none";	    

    if(mt_mode !="input")
	{
	    var attributes=annotation_data.getElementsByTagName('attribute');
	    for(var i=0;i<attributes.length;i++)
		{
		    var a =attributes[i];
		    t="A_"+a.getAttribute('tgt');
		    v=a.getAttribute('value');
		    f=$('MT_form')[t];
		    if(f.type=="checkbox")
			{		
			    if(v=="on")f.checked=1;
			}
		    else if(f.type=="select-one")
			{
			    f.value=v;
			}
		    else if(f.type=="textarea")
			{
			    f.value=v;
			}
		    else if(f.type=="text")
			{
			    f.value=v;
			}
		    else
			{
			    for( var fID=0;fID<f.length;fID++)
				{
				    var field=f[fID];
				    if(field.value==v)
					{
					    field.checked=true;
					    break;
					}
				}
			}
		}
	    var comments=annotation_data.getElementsByTagName('comment');
	    var comments_str="";
	    for(var iC=0;iC<comments.length;iC++)
		{ 
		    comments_str += comments[iC].getAttribute('text');
		}
	    $('Comments').value=comments_str;

	}

    var now = new Date();
    $('load_time').value=now.toUTCString();

}


