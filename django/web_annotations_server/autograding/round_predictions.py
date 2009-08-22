#!/usr/bin/env python
# Do this before running
#export DJANGO_SETTINGS_MODULE=web_annotations_server.settings
#export PYTHONPATH=/var/django2/web_annotations_server:/var/django2/:$PYTHONPATH

import os,sys,time
from mturk.models import *
from django.conf import settings
from xml.dom import minidom
from datastore import xmlmisc



def round_predictions(root):

    gt_file=os.path.join(root,'data.test')
    gt_url_file=os.path.join(root,'data.test_urls')
    preds_file=os.path.join(root,'preds.txt')
    report_fn=os.path.join(root,'preds.txt.report.txt')

    gt_lines=open(gt_file,'r').readlines();
    gt_values=[float(x.split('\t')[0]) for x in gt_lines];
    gt_urls=[ x.strip() for x in open(gt_url_file,'r').readlines()];

    pred_lines=open(preds_file,'r').readlines();
    pred_values=[float(x) for x in pred_lines];
    
    nGood=0.0
    nTotal=0.0
    correct_approvals=0.0
    correct_rejections=0.0
    incorrect_approvals=0.0
    incorrect_rejections=0.0

    correct_use=0.0
    correct_ignore=0.0
    incorrect_use=0.0
    incorrect_ignore=0.0
    final_predictions=[]
    for gt,raw_pred,url in map(None,gt_values,pred_values,gt_urls):
        if raw_pred<5:
            pred=3
        elif raw_pred>8.5:
            pred=10;
        else:
            pred=7

        is_error=False
        if abs(gt-pred)<0.1:
            nGood += 1
        else:
            is_error=True;
        nTotal += 1
        
        final_predictions.append(pred)

        if gt>=7:
            if pred<7:
                incorrect_rejections += 1
            else:
                correct_approvals += 1
        else:
            if pred>=7:
                incorrect_approvals += 1
            else:
                correct_rejections += 1

        if gt>=10:
            if pred<10:
                incorrect_ignore += 1
            else:
                correct_use += 1
        else:
            if pred>=10:
                incorrect_use += 1
            else:
                correct_ignore += 1

        if is_error:
            print gt, pred, raw_pred, url
    report_file=open(report_fn,'w')
    print >>report_file,"Accuracy:", nGood /nTotal;
    print >>report_file,"======="
    print >>report_file,"Correct_Approvals:",correct_approvals
    print >>report_file,"Correct_Rejections:", correct_rejections
    print >>report_file,"Incorrect_Approvals:", incorrect_approvals
    print >>report_file,"Incorrect_Rejections:", incorrect_rejections
    print >>report_file,"======="
    print >>report_file,"Correct_Ignore:",correct_ignore
    print >>report_file,"Correct_Use:", correct_use
    print >>report_file,"Incorrect_Use:", incorrect_use
    print >>report_file,"Incorrect_Ignore:", incorrect_ignore
    report_file.close()
    return (final_predictions,gt_urls)

if __name__=="__main__":
    root='/home/syrnick/daria/TreeExtra.1.2/data/bottles-p-2';
    round_predictions(root);





