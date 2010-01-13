
import scipy.io

from django.http import HttpResponse,Http404,HttpResponseRedirect
from django.shortcuts import render_to_response,get_object_or_404
from django.core.files.storage import FileSystemStorage

from models import *

import training

def show_models(request):
    sfm_models=get_models_list();
    return render_to_response('cv_models/sfm_3dmodel/models_list.html',{'models':sfm_models});


def show_model(request,model_id):
    model=get_object_or_404(LearnedModel,id=model_id);
    update_model_information(model);    
    return render_to_response('cv_models/sfm_3dmodel/show_model.html',{'m':model});
    

def model_info(request,model_id):
    m=get_object_or_404(LearnedModel,id=model_id);
    results={'id':m.id,'state':m.model_status};
    resp=HttpResponse()
    resp.write(yaml.dump(results))
    return resp


def create_model(request):
    code=request.REQUEST['code'];
    description=request.REQUEST['description'];
    parameters=request.REQUEST['parameters'];
    m=LearnedModel(code=code,name=description,
                   model_type=4,
                   model_arguments=parameters);
    m.save();
    m.location='/var/django/model_store/%d/' % m.id;
    os.makedirs(m.location);
    m.save();

    y_calibration=request.REQUEST['calibration']
    calibration=yaml.load(y_calibration);
    K=scipy.array(calibration['K']);
    KK=scipy.array(calibration['KK']);
    kc=scipy.array(calibration['kc']);
    scipy.io.savemat(os.path.join(m.location,'calibration.mat'),{'K':K,'KK':KK,'kc':kc});

    results={'id':m.id,'state':m.model_status};
    resp=HttpResponse()
    resp.write(yaml.dump(results))
    return resp
    
def train_model(request,model_id):
    m=get_object_or_404(LearnedModel,id=model_id);
    m.status=2; #Learning
    m.save();
    
    results={'id':m.id,'state':m.model_status};
    resp=HttpResponse()
    resp.write(yaml.dump(results))
    return resp

def download_model(request):
    m=get_object_or_404(LearnedModel,id=model_id);
    update_model_information(m);
    if len(m.model_files)==0:
        raise Http404;

    filename=os.path.join(m.model_loc,m.model_files[0]);
    outF=open(filename,'rb');
    content=outF.read();
    outF.close();
    return HttpResponse(content,mimetype="application/mat")



def create_blank_model(request):
    code=request.REQUEST['code'];
    description=request.REQUEST['description'];
    m=LearnedModel(code=code,name=description,
                   model_type=4);
    m.save();
    m.location='/var/django/model_store/%d/' % m.id;
    os.makedirs(m.location);
    m.save();

    results={'id':m.id,'state':m.model_status};
    resp=HttpResponse()
    resp.write(yaml.dump(results))
    return resp


def post_to_inbox(request,model_id):
    m=get_object_or_404(LearnedModel,id=model_id);

    uploaded_file=request.FILES['file'];
    fn=request.REQUEST['name'];
    original_name =uploaded_file.name
    loc=os.path.join(m.location,"inbox");
    if not os.path.exists(loc):
        os.makedirs(loc)
    storage = FileSystemStorage(loc);
    tgt=os.path.join(loc,fn);
    if storage.exists(tgt):
        storage.delete(tgt);
    fname=storage.save(os.path.join(loc,fn),uploaded_file);

    return HttpResponse("+")
    


def generate(request,model_id):
    m=get_object_or_404(LearnedModel,id=model_id);

    sfm_model = training.SfmModel(m.id,m.location,"");
    parameters = sfm_model.create_v1();
    m.model_arguments = parameters;
    
    m.state=2;
    m.save();

    return HttpResponse("+, Model is set into learning state")
    
