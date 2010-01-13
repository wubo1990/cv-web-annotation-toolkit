import os,re
from django.db import models
from cv_models.models import *
from django.conf import settings

from random import shuffle
from copy import copy

import yaml

        
class SfmModel(models.Model):

    model_filename = models.TextField(blank=True);
    model_preview = models.TextField(blank=True);
    best_surface_preview = models.TextField(blank=True);


    

def get_model_info(m_id):
    info={'id':m_id};
    return


def get_models_list():
    results=LearnedModel.objects.filter(model_type=4).all()
    for m in results:
        update_model_information(m);

    return results;


def update_model_information(m):
        data_root=os.path.join(m.location,'data');
        if not os.path.exists(data_root):
            return
        
        data_tags=os.listdir(data_root);
        if len(data_tags)==0:
            return
        tag=data_tags[0];
        img_dir=os.path.join(data_root,tag,'original');
        if not os.path.exists(img_dir):
            print "Failed to process model ",m.id
            return

        input_images=filter(lambda s:s.endswith('.jpg'),os.listdir(img_dir));
        m.input_images=input_images;
        s=copy(input_images);
        shuffle(s);
        m.input_image_samples=[];
        for ii in s[0:min(5,len(s))]:
            i2=os.path.join(img_dir,ii);
            i3=i2.replace(settings.MODEL_STORE_ROOT,'/models');
            m.input_image_samples.append(i3);
        
        models_root=os.path.join(m.location,'models');
        print models_root
        if not os.path.exists(models_root):
            return
        tags=filter(lambda s: not s.endswith('.iv'),os.listdir(models_root));
        iv_files=filter(lambda s: s.endswith('.iv'),os.listdir(models_root));        
        if len(tags)==0:
            return
        
        obj=tags[0];
        res_loc=os.path.join(models_root,obj);
        preview_fn=os.path.join(res_loc,'cam_and_object.jpg');
        files=os.listdir(res_loc);
        model_files=filter(lambda s:re.match('model_.*.mat',s),files);
        scaled_model_files=filter(lambda s:re.match('scaled_model_.*.mat',s),files);
        xml_model_files=filter(lambda s:re.match('model_.*.xml.tgz',s),files);
        scaled_xml_model_files=filter(lambda s:re.match('scaled_model_.*.xml.tgz',s),files);        
        preview_fn=os.path.join(res_loc,'cam_and_object.jpg');

        m.preview_fn = preview_fn.replace(settings.MODEL_STORE_ROOT,'/models');
        m.model_files=model_files
        m.scaled_model_files=scaled_model_files
        m.xml_model_files=xml_model_files
        m.scaled_xml_model_files=scaled_xml_model_files
        m.model_loc = res_loc.replace(settings.MODEL_STORE_ROOT,'/models');
        m.model_root = models_root.replace(settings.MODEL_STORE_ROOT,'/models');
        m.iv_files=filter(lambda s:not s.endswith('simplified.iv'),iv_files)
        simplified_iv_files=filter(lambda s: s.endswith('simplified.iv'),iv_files)            
        m.simplified_iv_files=simplified_iv_files


        object_clusters_fn=os.path.join(data_root,tag,'selected_clusters.txt')
        if os.path.exists(object_clusters_fn):
            cluster_ids=open(object_clusters_fn,'r').readlines();
            pmvs_root_options=['pmvs_c%02d' % int(c) for c in cluster_ids]
        else:
            pmvs_root_options=['pmvs']
        
        print pmvs_root_options
        pmvs_models=[];

        for pmvs_root_name in pmvs_root_options:
            pmvs_root=os.path.join(res_loc,pmvs_root_name);
            pmvs_model_locations=os.path.join(res_loc,pmvs_root_name,'models');

            if os.path.exists(pmvs_root):
                pmvs_model_imagesets=filter(lambda s:s.endswith('.imgset'),os.listdir(pmvs_root));
                pmvs_tags=[ s.replace('.imgset','') for s in pmvs_model_imagesets];

                model_location=pmvs_model_locations.replace(settings.MODEL_STORE_ROOT,'/models')

                for tag in pmvs_tags:
                    for sfx in ['', '.masked','.masked2','.masked3']:
                        poisson_rendering_dir=os.path.join(pmvs_model_locations,tag+sfx+'_rendered');
                        poisson_images_rendering_dir=os.path.join(poisson_rendering_dir,'images');
                        poisson_preview_flv=os.path.join(poisson_rendering_dir,'preview.flv');                                                   
                        if os.path.exists(poisson_images_rendering_dir):
                            images=os.listdir(poisson_images_rendering_dir);
                            pmvs_m={'title':'PMVS+Poisson @ '+tag+sfx+"("+pmvs_root_name +")",
                                    'tag':tag,
                                    'sfx':sfx,
                                    'model_location':model_location,
                                    'images':images,
                                    'img_location':poisson_images_rendering_dir.replace(settings.MODEL_STORE_ROOT,'/models')
                               };
                            if os.path.exists(poisson_preview_flv):
                                pmvs_m['preview_flv']='preview.flv';
                                pmvs_m['preview_location'] = poisson_rendering_dir.replace(settings.MODEL_STORE_ROOT,'/models')
                            pmvs_models.append(pmvs_m);
        m.pmvs_models=pmvs_models;
            
    
