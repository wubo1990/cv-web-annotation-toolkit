from django.contrib.sites.models import Site

import os,sys,time,shutil,getopt, random, shutil, re
import subprocess

from cv_models.models import *
from django.conf import settings


from xml.dom import minidom
#import session_results



"""Model layout
/data/OBJ_ID/images - undistorted images, masks, features
/data/OBJ_ID/imgaes/original - original images, masks in distorted images
/models/OBJ_ID/ - sfm working directory


"""

def ensure_dir(d):
    if not os.path.exists(d):
        os.makedirs(d)


class SfmModel():

    def __init__(self,id,location,parameters,target_class=None):
        self.id = id;
        self.location=location
        self.parameters=parameters
        self.target_class=target_class;

        self.parse_parameters();



    def get_stages(self):
        return ["prepare","extract_features","sfm","pmvs","render"];


    def parse_parameters(self):
        self.model_root=self.location;


    def create_v1(self):
        imgs=os.path.join(self.model_root,"inbox","images.tgz")
        print imgs
        originals_path=os.path.join(self.model_root,"data","sfm","original")
        ensure_dir(originals_path)
        
        os.system("tar xvzCf %s %s" % (originals_path,imgs));
        os.system("mv %s/*/*.jpg %s" % (originals_path,originals_path));
            
        calibration=os.path.join(self.model_root,"inbox","calibration.mat");
        calibration_tgt=os.path.join(self.model_root,"calibration.mat");
        shutil.copyfile(calibration,calibration_tgt);

        camera_locations=os.path.join(self.model_root,"inbox","camera_locations.txt");
        camera_locations_tgt=os.path.join(self.model_root,"camera_locations.txt");
        if os.path.exists(camera_locations):
            shutil.copyfile(camera_locations,camera_locations_tgt);

        os.system("chmod -R 777 %s" % (self.model_root));

        parameters="--server=NONE --session=NONE --target=sfm --features=sift"

        return parameters


    def build_model(self):

        model_root=self.location;
        data_root=os.path.join(model_root,'data');
        ensure_dir(data_root)            
        
        srv=None
        session_code=None
        target_class=None


    
        features="sift";
        calibration_model=os.path.join(model_root,'../scale_calibration_model.mat');
        MCR_root='/opt/MATLAB/MATLAB_Compiler_Runtime/v79'

        print "Parameters:",self.parameters
        optlist, args = getopt.getopt(self.parameters, "", ["server=","session=","target=","features=","calibration_model="])
        for (field, val) in optlist:
            if field == "--server":
                srv=val;
            elif field == "--session":
                session_code=val
            elif field == "--target":
                self.target_class=val
            elif field == "--features":
                features=val
            elif field == "--calibration_model":
                calibration_model=val
                if not os.path.exists(calibration_model):
                    calibration_model=os.path.join(model_root,calibration_model);
                    
                
        if self.target_class is None:
            self.target_class=session_code.split("-")[1];

        models_dir=os.path.join(model_root,'models');
        ensure_dir(models_dir)
    
        if not srv:
            srv="NONE"
        if not session_code:
            session_code="NONE"

    
        bin_rt='/home/sorokin2/ros/intel/alvaro/'
        bin_rt2='/home/sorokin2/ros/intel/alvaro_v2/'
        ld_path = "export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:`rospack find opencv_latest`/opencv/lib:/home/sorokin2/ros/intel/alvaro/utils/"

        self.expected_model_file = os.path.join(models_dir,self.target_class,'model_'+self.target_class+'.mat')

        
        #self.prepare_evaluation_videos()
        #return

        self.select_best_models()
        return

        ##Prepare data
        cmd="""%s; octave --eval "cd %s;make_model_steps_1_prepare('%s', '%s','%s','%s','%s')" """ % (
            ld_path,bin_rt,bin_rt,model_root,self.target_class, srv, session_code)
        print cmd
        sts=os.system(cmd)


        ##Extract features
        self.extract_features(bin_rt,model_root, srv, session_code, features)
        print cmd
        sts=os.system(cmd)    


        ##Build bundler model (it'll include matching for now)
        cmd="""%s; octave --eval "cd %s;make_model_steps_4_sfm_bundler('%s', '%s','%s','%s','%s')" """ % (
            ld_path,bin_rt,bin_rt,model_root,self.target_class, srv, session_code)
        print cmd
        sts=os.system(cmd)    



        """ Scale estimation: """
        camera_locations_file=os.path.join(model_root,'camera_locations.txt')
        scale_output_file = os.path.join(models_dir,self.target_class,'bundle.out.scale')
        
        if os.path.exists(camera_locations_file):
            """ Attempt to use known camera locations """
            cmd="""%s; octave --eval "cd %s;make_model_steps_4c_estimate_scale_from_camera_locations('%s', '%s','%s')" """ % (
                ld_path,bin_rt,bin_rt,model_root,self.target_class)
            print cmd
            sts=os.system(cmd)


        if not os.path.exists(scale_output_file):
            """ Attempt to use calibration objects """
            if not os.path.exists(calibration_model):
                print "ERROR: no calibration model, skipping scale estimation"
            else:
                features_dir=os.path.join(model_root,'data',self.target_class)
                bundler_reconstruction_file = os.path.join(models_dir,self.target_class,'bundle.out')

                ##Scale the model using calibration target
                cmd="""%s;%s/run_compute_scale.sh %s %s %s %s %s""" %(
                    ld_path,bin_rt2,MCR_root, features_dir, calibration_model, bundler_reconstruction_file, scale_output_file)
                print cmd
                sts=os.system(cmd)    


        ##Build pmvs model and meshes
        cmd="""%s; octave --eval "cd %s;make_model_steps_5_pmvs('%s', '%s','%s','%s','%s')" """ % (
            ld_path,bin_rt,bin_rt,model_root,self.target_class, srv, session_code)
        print cmd
        sts=os.system(cmd)    


        ##Create scaled model and scaled meshes
        cmd="""%s; octave --eval "cd %s;make_model_5b_scaled_models_and_meshes('%s', '%s','%s','%s','%s')" """ % (
            ld_path,bin_rt,bin_rt,model_root,self.target_class, srv, session_code)
        print cmd
        sts=os.system(cmd)


        self.prepare_evaluation_videos()





    def prepare_evaluation_videos(self):

        print "PREPARING EVALUATION VIDEOS"

        data_root=os.path.join(self.model_root,'data',self.target_class);
        object_clusters_file=os.path.join(data_root,'selected_clusters.txt');
        if os.path.exists(object_clusters_file):
            use_clusters=True;
            fCls=open(object_clusters_file,'r')
            clusters=[int(s) for s in fCls.readlines() if len(s.strip())>0];
            suffix_list=['.masked','.masked2','.masked3'];
        else:
            use_clusters=False
            clusters=['']
            suffix_list=['']

        for c in clusters:
            if use_clusters:
                pmvs_root=os.path.join(self.model_root,'models',self.target_class,'pmvs_c%02d' % c);
            else:
                pmvs_root=os.path.join(self.model_root,'models',self.target_class,'pmvs');
            evaluation_root=os.path.join(pmvs_root,'evaluation');
            ensure_dir(evaluation_root)
            evaluation_movies_root=os.path.join(evaluation_root,'grading_movies');
            ensure_dir(evaluation_movies_root)
            print evaluation_movies_root

            cmd1='ls %s | grep options.txt | sed -e /imgset/d>%s/tags' %(pmvs_root,pmvs_root)
            os.system(cmd1);
            tags=map(lambda s:s.strip(),open('%s/tags' % pmvs_root,'r').readlines());
            fTasks=open(os.path.join(evaluation_movies_root,'tasks.txt'),'w');

            for t in tags:
                for sfx in suffix_list:
                    if use_clusters:
                        movie_id="m%d_%s_c%02d_%s%s" %(self.id,self.target_class,c,t,sfx);
                    else:
                        movie_id="m%d_%s_%s" %(self.id,self.target_class,t);
                    cmd2='cp %s/models/%s%s_rendered/preview.flv %s/%s.flv' % (pmvs_root,t,sfx,evaluation_movies_root,movie_id);
                    movie_fn = '%s/models/%s%s_rendered/preview.flv' % (pmvs_root,t,sfx);
                    if os.path.exists(movie_fn):
                        os.system(cmd2);        
                        print >>fTasks,"""<item id="%s" type="video" src="/frames/model-evaluation-movies/%s.flv"/> """ %(movie_id,movie_id)
            fTasks.close()


    def select_best_models(self):

        print "SELECTING BEST MODELS"
        model_root=os.path.join(self.model_root,'models');
        model_root2=os.path.join(self.model_root,'models',self.target_class);

        best_models_fn=os.path.join(model_root,'best_models.txt')
        if not os.path.exists(best_models_fn):
            print "Missing file", best_models_fn
            return

        best_selected_models=open(best_models_fn,'r').readlines();
        for m in best_selected_models:
            (group,score,selection)=m.split(' ')
            selection=selection.replace(group+'_','').strip()
            cluster_object=re.match("^m(?P<model_id>.*)_(?P<target_class>.*)_c(?P<cluster_id>.*)$",group)
            if cluster_object:
                model_id=cluster_object.group('model_id')
                cluster_id=cluster_object.group('cluster_id')
                target_class=cluster_object.group('target_class')
                object_id='objectM%s_c%s' %(model_id,cluster_id);
                input_model_xml=os.path.join(model_root2,'scaled_model_%s_c%s.xml' %(target_class,cluster_id));
                output_model_xml=os.path.join(model_root,'%s.xml' % object_id)

		xmldoc = minidom.parse(input_model_xml);
		model=xmldoc.getElementsByTagName("Model")[0];
                model.setAttribute("name",object_id);

                fOut=open(output_model_xml,'w');
                xmldoc.writexml(fOut);
                fOut.close()
                
            print group,selection,score


    def extract_features(self,bin_rt,model_root,srv, session_code, feature_type):
        if feature_type=="sift":
            pass #The bundler will do it for us

        elif feature_type=="surf":
            #DOESN"T WORK
            img_dir=os.path.join(model_root,'data',self.target_class);
            image_names=filter(lambda s:s.endswith('.jpg'),os.listdir(img_dir));
            for img in image_names:
                image_fn = os.path.join(img_dir,img);
                features_fn = os.path.join(img_dir,img.replace('.jpg','.key'));
                gzip_features_fn = os.path.join(img_dir,img.replace('.jpg','.key.gz'));
                if os.path.exists(gzip_features_fn):
                    continue
                if os.path.exists(features_fn):
                    continue

                cmd="rosrun autonomous_model_builder cv_surf %s %s 100" %(image_fn,features_fn)
                print cmd
                p = subprocess.Popen(cmd,shell=True);
                sts = os.waitpid(p.pid, 0)[1]
                #p = subprocess.Popen("gzip %s" % features_fn, shell=True);
                #sts = os.waitpid(p.pid, 0)[1]
        elif feature_type=="fast_calonder":
            img_dir=os.path.join(model_root,'data',self.target_class);
            image_names=filter(lambda s:s.endswith('.jpg'),os.listdir(img_dir));
            for img in image_names:
                image_fn = os.path.join(img_dir,img);
                features_fn = os.path.join(img_dir,img.replace('.jpg','.key'));
                gzip_features_fn = os.path.join(img_dir,img.replace('.jpg','.key.gz'));
                if os.path.exists(gzip_features_fn):
                    continue
                if os.path.exists(features_fn):
                    continue

                cmd="cd `rospack find autonomous_model_builder`;./src/fex_fast_calonder.py --image=%s --features=%s --rtc=`rospack find autonomous_model_builder`/test_data/current.rtc --threshold=3" %(image_fn,features_fn)
                print cmd
                p = subprocess.Popen(cmd,shell=True);
                sts = os.waitpid(p.pid, 0)[1]        
        else:
            raise "Error: unknown feature type";














def prepare_data(m):
    return True

def build_model(m):
    print "Building model",m
    m.model_status=2; #Learning
    m.save();


    #Download results from the server
    parameters=[];
    if m.data_sources.count()>0:
        src = m.data_sources[0]
        if src.source_session is not None:
            srv=Site.objects.get_current().domain
            session_code=src.source_session.code
        else:
            src_parameters=src.source_ref.split(' ');
            parameters.extend(src_parameters);

    target_class = None
    if m.targets.count()>0:
        target = m.targets.all()[0]
        target_class=target.target_code;

    model_params = m.model_arguments.split(' ');
    parameters.extend(model_params);

    sfm_model = SfmModel(m.id,m.location,parameters,target_class);

    sfm_model.build_model();
    
    if os.path.exists(sfm_model.expected_model_file):
        m.model_status=3; #Learning-complete
        m.save();
    else:
        print "Can't find",sfm_model.expected_model_file
    


