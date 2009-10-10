from django.contrib.sites.models import Site

import os,sys,time,shutil,getopt, random

from cv_models.models import *
from django.conf import settings

import session_results



"""Model layout
/data/OBJ_ID/images - undistorted images, masks, features
/data/OBJ_ID/imgaes/original - original images, masks in distorted images
/models/OBJ_ID/ - sfm working directory


"""


def ensure_dir(d):
    if not os.path.exists(d):
        os.makedirs(d)



def prepare_data(m):
    return True

def build_model(m):
    print "Building model",m
    m.model_status=2; #Learning
    m.save();

    model_root=m.location;
    data_root=os.path.join(model_root,'data');
    ensure_dir(data_root)            

    #done_fn=os.path.join(data_root,'done.txt');
    #if os.path.exists(done_fn):
    #    return True;

    parameters=[];
    srv=None
    session_code=None
    target_class=None
    
    #Download results from the server
    if m.data_sources.count()>0:
        src = m.data_sources[0]
        if src.source_session is not None:
            srv=Site.objects.get_current().domain
            session_code=src.source_session.code
        else:
            src_parameters=src.source_ref.split(' ');
            parameters.extend(src_parameters);

    if m.targets.count()>0:
        target = m.targets.all()[0]
        target_class=target.target_code;

    model_params = m.model_arguments.split(' ');
    parameters.extend(model_params);
            
    optlist, args = getopt.getopt(parameters, "", ["server=","session=","target="])
    for (field, val) in optlist:
        if field == "--server":
            srv=val;
        elif field == "--session":
            session_code=val
        elif field == "--target":
            target_class=val            

                
    if target_class is None:
        target_class=session_code.split("-")[1];

    models_dir=os.path.join(model_root,'models');
    ensure_dir(models_dir)
    


    if not srv:
        srv="NONE"
    if not session_code:
        session_code="NONE"


    bin_rt='/home/sorokin2/ros/intel/alvaro/'
    #bin_rt='~/ros/intel/alvaro/'
    ld_path = "export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:`rospack find opencv_latest`/opencv/lib"
    cmd="""%s; octave --eval "cd %s;make_model_only('%s', '%s','%s','%s','%s')" """ % (
        ld_path,bin_rt,bin_rt,model_root,target_class, srv, session_code)

    print cmd
    sts=os.system(cmd)

    if os.path.exists(os.path.join(model_root,target_class,'model_'+target_class+'.mat')):
        m.model_status=3; #Learning-complete
        m.save();
