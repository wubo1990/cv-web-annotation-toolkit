#!/usr/bin/env python

"""

Usage: demo_engine.py --action=<action> --submission=<file_name> --work_root=<submission_root> --report=<report_filename> --dataset_root=<dataset_location>

action:
   check
   score   
"""

import os,sys,getopt,random,re

from xml.dom import minidom

from string import Template

def usage(progname):
    print __doc__ % vars()



def writeError(report,msg):
    fError=open(report+'.error','a')
    print >>fError,msg
    fError.close()

def check_classifications_format(filename,err_fcn):
    pattern = re.compile("^([^\ \t]+)([ \t]+)([\-\.1234567890]+)\n$")

    f=open(filename,'r');
    for i,l in enumerate(f.readlines()):
        if not pattern.match(l):
            err_fcn("Detections file has wrong format. Expected <image> <confidence>")
            return False
    return True
    
def check_detections_format(filename,err_fcn):
    N="([\-\.1234567890]+)"
    S="([ \t]+)"
    pattern = re.compile("^([^\ \t]+)" + S + N + S + N + S + N + S + N + S + N + "\n$")

    f=open(filename,'r');
    for i,l in enumerate(f.readlines()):
        if not pattern.match(l):
            err_fcn("Detections file has wrong format. Expected <image> <confidence> <left> <top> <width> <height>")
            return False
    return True


    
def main(argv):
    optlist, args = getopt.getopt(argv[1:], "", ["help", "action=", "submission=", "report=",
                                                 "dataset_root=","work_root=","challenge=","setname=","devkit="])

    action=None
    submission=None
    dataset_root=None
    work_root=None
    report=None
    challenge=None
    setname=None
    devkit_root=None;
    
    for (field, val) in optlist:
        if field == "--help":
            usage(progname)
            return
        elif field == "--action":
            action=val
        elif field == "--submission":
            submission=val
        elif field == "--dataset_root":
            dataset_root=val
        elif field == "--work_root":
            work_root=val
        elif field == "--devkit":
            devkit_root=val;
        elif field == "--report":
            report=val
        elif field== "--challenge":
            challenge=val;
        elif field== "--setname":
            setname=val; #val,test

    hasError=False

    print report
    fReport=open(report,'w')

    print >>fReport,"Checking submission"
    print >>fReport,"\tSubmission file: %s" % submission
    print >>fReport,"\tWorking directory: %s" % work_root
    print >>fReport,"Extracting submission"

    if submission.endswith('.tgz') or submission.endswith('.tar.gz'):
        status=os.system("tar xvzCf %s %s" % (work_root,submission));
        if status !=0 :
            print >>fReport,"Failed to extract the file. It appears to be a gzipped tar file, but tar xvzf failed."
            writeError(report,"Failed to extract the file. It appears to be a gzipped tar file, but tar xvzf failed.")
            hasError=True
    elif submission.endswith('.tar'):
        status = os.system("tar xvCf %s %s" % (work_root,submission));
        if status !=0 :
            print >>fReport,"Failed to extract the file. It appears to be a plain tar file, but tar failed."
            writeError(report,"Failed to extract the file. It appears to be a plain tar file, but tar failed.")
            hasError=True
    else:
        print >>fReport,"Unknown file extension."
        print >>fReport,"\tHint: Use '.tgz' or '.tar.gz' for compressed files"
        print >>fReport,"\tHint: Use '.tar' for uncompressed files"
        writeError(report,"Unknown file extension. Use .tgz or .tar.gz ")
        hasError=True

    if hasError:
        return

    results_dir=os.path.join(work_root,'results');
    if not os.path.exists(results_dir):
        print >>fReport,"\tMissing 'results' folder. Did you change directory structure from the dev kit?"
        writeError(report,"Missing 'results' folder in the archive")
        hasError=True        
    
    if hasError:
        return

    challenge_dir=os.path.join(results_dir,challenge);
    if not os.path.exists(challenge_dir):
        print >>fReport,"\tMissing 'results/%s' folder in the archive" % challenge_dir
        writeError(report,"Missing 'results/%s' folder in the archive" % challenge_dir)
        hasError=True        

    if hasError:
        return

    print >>fReport,"Extraction complete."
    print >>fReport,"Checking submission."


    has_challenge_data={};
    
    object_classes='person,bird,cat,cow,dog,horse,sheep,aeroplane,bicycle,boat,bus,car,motorbike,train,bottle,chair,diningtable,pottedplant,sofa,tvmonitor'.split(',')

    by_class_challenges=[(1,'Main/comp1_cls_${setname}_${class}.txt'),
                (2,'Main/comp2_cls_${setname}_${class}.txt'),
                (3,'Main/comp3_det_${setname}_${class}.txt'),
                (4,'Main/comp4_det_${setname}_${class}.txt')]
    single_file_challenges=[
                (7,'Layout/comp7_layout_${setname}.xml'),
                (8,'Layout/comp8_layout_${setname}.xml')
                ]
    by_image_challenges=[
        (5,'Segmentation/comp5_${setname}_cls','${challenge}/ImageSets/Segmentation/${setname}.txt'),
        (6,'Segmentation/comp6_${setname}_cls','${challenge}/ImageSets/Segmentation/${setname}.txt')
        ]

    def err_fcn(msg):
        writeError(report,msg);
        print >>fReport,msg

    for (iC,template) in by_class_challenges:
        hasAnyClasses=False
        hasAllClasses=True
        missing_classes=[]
        detected_classes=[]
        presence_by_class={};
        for c in object_classes:
            expected_fn=Template(template).substitute({ 'setname': setname, 'class':c});
            print expected_fn, template
            expected2_fn=os.path.join('results',challenge,expected_fn);
            expected_full_fn=os.path.join(work_root,expected2_fn);
            if os.path.exists(expected_full_fn):
                if iC==1 or iC==2:
                    format_check_ok=check_classifications_format(expected_full_fn,err_fcn);
                if iC==3 or iC==4:
                    format_check_ok=check_detections_format(expected_full_fn,err_fcn);
                if format_check_ok:
                    hasAnyClasses=True
                    detected_classes.append(c)
                    presence_by_class[c]=True;
                else:
                    hasAllClasses=False
                    missing_classes.append(c)
                    presence_by_class[c]=False;
                    hasError=True                
                    err_fcn("Error in a file format");
            else:
                hasAllClasses=False
                missing_classes.append(c)
                presence_by_class[c]=False;
        if hasAnyClasses:
            if hasAllClasses:
                print >>fReport,"Challenge %d.+++ Submitted. All results present." % iC;
                has_challenge_data[iC]=True
            else:
                print >>fReport,"Challenge %d. Some results present. Found %d out of %d classes:" % (iC,len(detected_classes),len(object_classes))
                has_challenge_data[iC]=True
                for c in object_classes:
                    if presence_by_class[c]:
                        print >>fReport,"\t%s ... Found" % c
                    else:
                        print >>fReport,"\t%s ... Missing" % c
        else:
            print >>fReport,"Challenge %d. No results present." % iC;
            has_challenge_data[iC]=False

    for (iC,folder_template,imageset_file_tempalte) in by_image_challenges:
        expected_fn=Template(folder_template).substitute({ 'setname': setname});
        expected2_fn=os.path.join('results',challenge,expected_fn);
        expected_full_fn=os.path.join(work_root,expected2_fn);
        if os.path.exists(expected_full_fn):
            imageset_fn=os.path.join(devkit_root,Template(imageset_file_tempalte).substitute({ 'setname': setname,'challenge':challenge}));
            missing_files=[];
            detected_files=[];
            if not os.path.exists(imageset_fn):
                print >>fReport,"Challenge %d. Missing imageset files in the DEVKIT." % (iC)
                writeError(report,"Challenge %d. Missing imageset files in the DEVKIT." % (iC))
                hasError=True                
                has_challenge_data[iC]=False
                continue

            image_names=open(imageset_fn,'r').readlines()

            for img_name in image_names:
                img_name=img_name.strip();
                img_file_name=os.path.join(expected_full_fn,img_name+'.png');
                if not os.path.exists(img_file_name):
                    missing_files.append(img_name)
                else:
                    detected_files.append(img_name)
            if len(detected_files)==0:
                print >>fReport,"Challenge %d. Not submitted - no images (looking for png images in folder %s)" % (iC,expected2_fn);
                print >>fReport,"\t\tE.g. %s/%s.png" %(expected2_fn,missing_files[0])
                has_challenge_data[iC]=False
            elif len(missing_files)>0:
                has_challenge_data[iC]=False
                print >>fReport,"Challenge %d. Missing some of the result files. Check that all results images have been generated. Here're some of the missing results." % (iC)
                writeError(report,"Challenge %d. Missing some of the result files. Check that all results images have been generated. Here're some of the missing results." % (iC))
                hasError=True                
                for i,f in enumerate(missing_files):
                    print >>fReport,"\tMissing %s/%s.png" % (expected2_fn,f)
                    if i>=9:
                        print >>fReport,"\tMissing %d other files" % (len(missing_files)-i)
                        break
            else:
                has_challenge_data[iC]=True
                print >>fReport,"Challenge %d.+++ Submitted. All required images are present." % (iC);                    
        else:
            print >>fReport,"Challenge %d. Not submitted (looking for folder %s)" % (iC,expected2_fn);
            has_challenge_data[iC]=False
    if hasError:
        return
    
    for (iC,template) in single_file_challenges:
        expected_fn=Template(template).substitute({ 'setname': setname});
        print template,expected_fn
        expected2_fn=os.path.join('results',challenge,expected_fn);
        expected_full_fn=os.path.join(work_root,expected2_fn);
        if os.path.exists(expected_full_fn):

            try:
                xmldoc = minidom.parse(expected_full_fn);
            except:
                print >>fReport,"Challenge %d. Error: Failed to parse XML document %s." % (iC,expected2_fn);
                writeError(report,"Challenge %d. Error: Failed to parse XML document %s." % (iC,expected2_fn));
                has_challenge_data[iC]=False
                continue
            
            layout_elements=xmldoc.getElementsByTagName("layout");
            if len(layout_elements)==0:
                print >>fReport,"Challenge %d. Error: The XML document (%s) has no 'layout' elements." % (iC,expected2_fn);
                writeError(report,"Challenge %d. Error: The XML document (%s) has no 'layout' elements." % (iC,expected2_fn))
                has_challenge_data[iC]=False
                continue
                
            print >>fReport,"Challenge %d.+++ Submitted. Submission file present." % iC;
            has_challenge_data[iC]=True
        else:
            print >>fReport,"Challenge %d. Not submitted (looking for %s)" % (iC,expected2_fn);
            has_challenge_data[iC]=False


    hasAnyChallenge=False
    for (c,s) in has_challenge_data.items():
        if s:
            hasAnyChallenge=True

    if not hasAnyChallenge:
        print >>fReport,"Could not find submission to any of the challenges"
        print >>fReport,"Submission check failed."
        writeError(report,"Could not find submission to any of the challenges")
        return


    challenges_fn=os.path.join(work_root,"challenges.txt");
    challenges_file=open(challenges_fn,'w')
    for c in range(1,9):
        if has_challenge_data[c]:
            print >>challenges_file,c
        else:
            print >>challenges_file,0
    challenges_file.close();
    
    print >>fReport,"Submission check complete."
    print >>fReport,"Task is ready for evaluation."

    fReport.close();


if __name__=="__main__":
    main(sys.argv);
