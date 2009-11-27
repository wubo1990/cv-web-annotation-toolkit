#!/usr/bin/env python

"""

Usage: demo_engine.py --action=<action> --submission=<file_name> --work_root=<submission_root> --report=<report_filename> --dataset_root=<dataset_location>

action:
   check
   score   
"""

import os,sys,getopt,random

def usage(progname):
    print __doc__ % vars()



def writeError(report,msg):
    fError=open(report+'.error','a')
    print >>fError,msg
    fError.close()
    
def main(argv):
    optlist, args = getopt.getopt(argv[1:], "", ["help", "action=", "submission=", "report=",
                                                 "dataset_root=","work_root="])

    action=None
    submission=None
    dataset_root=None
    work_root=None
    report=None
    
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
        elif field == "--report":
            report=val

    hasError=False

    fReport=open(report,'w')

    print >>fReport,"Checking submission"
    print >>fReport,"\tSubmission file: %s" % submission
    print >>fReport,"\tWorking directory: %s" % work_root
    print >>fReport,"Extracting submission"

    if submission.endswith('.tgz') or submission.endswith('.tar'):
        os.system("tar xvzCf %s %s" % (work_root,submission));
    elif submission.endswith('.tar'):
        os.system("tar xvCf %s %s" % (work_root,submission));
    else:
        print >>fReport,"Unknown file extension."
        print >>fReport,"\tHint: Use '.tgz' or '.tar.gz' for compressed files"
        print >>fReport,"\tHint: Use '.tar' for uncompressed files"
        writeError(report,"Unknown file extension")
        hasError=True

    if hasError:
        return

    print >>fReport,"Extraction complete."
    print >>fReport,"Evaluating."


    fFinal=open(report+'.final_score','w');
    fScore=open(report+'.score','w');
    scores=[ random.uniform(0,1) for x in range(10)]
    for i,s in enumerate(scores):
        print >>fScore,s,i
    print >>fFinal,sum(scores)/len(scores)
    print >>fReport,"Evaluation done."
    
    fReport.close();


if __name__=="__main__":
    main(sys.argv);
