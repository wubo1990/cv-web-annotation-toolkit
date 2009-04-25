function flag_click(ref_annotation,flag_name){
    flag_id="flag_"+flag_name+"_"+ref_annotation;
    im_flag_id="im_flag_"+flag_name+"_"+ref_annotation;
    
    if( $(im_flag_id).hasClassName("flag_on")){
	$(im_flag_id).addClassName("flag_updating");
	$(im_flag_id).removeClassName("flag_on");
	do_flag_url="/datastore/annotation/"+ ref_annotation +"/unflag/"+flag_name+"/";
	new Ajax.Updater(flag_id, do_flag_url);
    }else{
	$(im_flag_id).addClassName("flag_updating");
	$(im_flag_id).removeClassName("flag_off");
	do_flag_url="/datastore/annotation/"+ ref_annotation +"/flag/"+flag_name+"/";
	new Ajax.Updater(flag_id, do_flag_url);
    }

}

function create_flag(ref_annotation,flag_name,flag_value){
    //document.write("<a href='/datastore/annotation/"+ ref_annotation +"/flag/"+flag_name+"/' target='_rcd_flag'><img src='/code/images/ico/flag_"+flag_name+".gif'></a>");
    flag_id="flag_"+flag_name+"_"+ref_annotation;
    click_cmd='flag_click('+ref_annotation+',"'+flag_name+'");';
    //document.write("<img class='flag_off' id='"+flag_id+"' src='/code/images/ico/flag_"+flag_name+".gif' onclick='"+click_cmd+"'/>");
    if(flag_value>0){
	state="flag_on";
    }else{
	state="flag_off";
    }
    document.write("<td><div id='"+flag_id+"'> <img class='"+state+"' id='im_"+flag_id+"' src='/code/images/ico/flag_"+flag_name+".gif' onclick='"+click_cmd+"'/></div></td>");
}
