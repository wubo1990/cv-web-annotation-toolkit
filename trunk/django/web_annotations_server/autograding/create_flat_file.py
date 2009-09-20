#!/usr/bin/env python
# Do this before running
#export DJANGO_SETTINGS_MODULE=web_annotations_server.settings
#export PYTHONPATH=/var/django2/web_annotations_server:/var/django2/:$PYTHONPATH

import os,sys,time
from mturk.models import *
from django.conf import settings
from xml.dom import minidom
from datastore import xmlmisc

def extract_submission_features(submission):
    x_str = submission.get_xml_str();
    #print x_str
    if x_str=="":
        return [0, "?", "?", "?", "?", "?", "?", "?"];

    has_data=1;
    x_doc = minidom.parseString(x_str);
    meta=x_doc.getElementsByTagName("meta")[0];    

    lt=float(meta.getAttribute("load_time"))/1000;
    st=float(meta.getAttribute("submit_time"))/1000;
    duration=st-lt;

    num_poly=len(x_doc.getElementsByTagName("polygon"));
    num_bbox=len(x_doc.getElementsByTagName("bbox"));
    num_pts=len(x_doc.getElementsByTagName("pt"));

    pt_times=[];
    for p in x_doc.getElementsByTagName("pt"):
        t=float(p.getAttribute("ct"))/1000;
        pt_times.append(t);
    if len(pt_times)>1:
        pt_times.sort();
        time_difference=[];
        for i in range(0,len(pt_times)-1):
            time_difference.append(pt_times[i+1]-pt_times[i]);
        time_difference.sort();
                
        median_time=time_difference[int(round(len(time_difference)/2))]
    else:
        median_time="?"

    if num_poly==0:
        num_poly_fixed=1
        pts_per_poly=(num_pts-2*num_bbox)/num_poly_fixed;
    else:
        num_poly_fixed=num_poly
        pts_per_poly=(num_pts-2*num_bbox)/num_poly_fixed;

    return [has_data, duration, num_poly, num_bbox, num_bbox-num_poly, num_pts-2*num_bbox, median_time,pts_per_poly];
    
def get_attribute_list():
    return \
"""has_data: 0,1.
total_time: cont.
num_poly: cont.
num_bbox: cont.
diff_num_bbox_num_poly: cont.
num_poly_points: cont.
time_per_point: cont.
pts_per_poly: cont."""

def write_dataset(root,examples, attr_list, split_ratios):
    random.seed(1234);
    random.shuffle(examples);
    nTrain=int(len(examples)*split_ratios[0]);
    nVal=int(len(examples)*split_ratios[1]);
    nTest=len(examples)-nTrain-nVal;

    train_set=examples[0:nTrain];
    val_set=examples[nTrain:nTrain+nVal];
    test_set=examples[nTrain+nVal:];

    attr_fn=os.path.join(root,'data.attr')
    train_fn=os.path.join(root,'data.train')
    val_fn=os.path.join(root,'data.valid')
    test_fn=os.path.join(root,'data.test')
    test_url_fn=os.path.join(root,'data.test_urls')

    save_to_file(train_set,train_fn);
    save_to_file(val_set,val_fn);
    save_to_file(test_set,test_fn);

    save_url_to_file(test_set,test_url_fn);

    print_attributes_file(attr_fn,attr_list)


def save_to_file(examples , fn):
      f=open(fn,'w')
      for label,features,url,submission_id in examples:
          f.write(str(label))
          for fv in features:
              f.write("\t")
              f.write(str(fv))
          f.write("\n")
      f.close()

def save_url_to_file(examples , fn):
      f=open(fn,'w')
      for label,features,url,submission_id in examples:
          f.write(str(submission_id))
          f.write("\t")
          f.write(url)
          f.write("\n")
      f.close()

def print_attributes_file(fn,attr_list):
      f=open(fn,'w')
      f.write("label: cont (class).\n")
      f.write(attr_list)
      f.close()

def create_grading_flat_file(session_code,feature_dir, split_ratios):
	session=Session.objects.get(code=session_code);
        print session
        if not os.path.exists(feature_dir):
            os.makedirs(feature_dir);

        examples=[];
        for submission in session.submittedtask_set.all():
            
            print submission.id,submission.final_grade,
            features=extract_submission_features(submission);
            print features
            url="http://vm7.willowgarage.com/mt/adjudicate/%s/%d/" % (session_code,submission.id)
            examples.append((submission.final_grade, features, url, submission.id))
            #for grade in task.

        attr_list=get_attribute_list();

        write_dataset(feature_dir,examples, attr_list,split_ratios)
        return

if __name__=="__main__":
    #create_grading_flat_file('bottles-p-3','/home/syrnick/daria/TreeExtra.1.2/data');
    create_grading_flat_file('bottles-p-2','/home/syrnick/daria/TreeExtra.1.2/data/bottles-p-2/',[0.5,0.25,0.25]);
