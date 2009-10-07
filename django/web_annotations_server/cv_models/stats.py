import os,re

from models import *

def get_model_performance_stats(m):
    report={'targets':[1,2,3],'tests':['trainval','test'],'perf_metric':'AP','perf_values':[ {'t':1,'v':[1,2]},{'t':2,'v':[3,4]},{'t':3,'v':[5,6]}]};

    perf_values={};
    tgts={};
    tests={};
    if m.model_type == 1: #PF HOG
        report={};
        test_file_location=os.path.join(m.location,"data/results/model-%d-ds/Main/" % m.id);
        for t in m.targets.all():
            tgts[t.target_code]=1;
            #files=os.listdir(test_file_location+"eval_rpt_"+ t.target_code +"*.txt");
            files=os.listdir(test_file_location);
            for f in files:
                ctx=re.match("^eval_rpt_"+t.target_code+"_(\w+).txt",f)
                if ctx:
                    test_id=ctx.group(1);
                    tests[test_id]=1;
                    rpt_fn=os.path.join(test_file_location,f);
                    hF=open(rpt_fn,'r');
                    ctx2=re.match("^w_box_regression:([\w\d\.]+)$",hF.readlines()[-1]);
                    perf=ctx2.group(1);
                    print perf
                    perf_values[(t.target_code,test_id)]=perf
                    hF.close()
        report['targets']=tgts;
        report['tests']=tests;
        report['perf_metric']='AP';
        perf_values_list=[]
        for t in m.targets.all():
            v=[];
            for tst in tests:
                v.append(perf_values.get((t.target_code,tst),None))
            perf_values_list.append({'t':t.target_code,'v':v});
        report['perf_values']=perf_values_list ;
        print perf_values_list
    
    return report;
