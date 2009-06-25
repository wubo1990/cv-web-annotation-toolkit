function eval_comp5(VOClocation,results_root,report_fn,compid)

% change this path if you install the VOC code elsewhere
if ~exist('compid','var')
   compid='comp5';
end

devkitroot = VOClocation
% initialize VOC options
VOCinit;

VOCopts.resdir=[results_root VOCopts.dataset '/'];
VOCopts.clsrespath=[VOCopts.resdir 'Main/%s_cls_' VOCopts.testset '_%s.txt'];
VOCopts.detrespath=[VOCopts.resdir 'Main/%s_det_' VOCopts.testset '_%s.txt'];
VOCopts.seg.clsresdir=[VOCopts.resdir 'Segmentation/%s_%s_cls'];
VOCopts.seg.instresdir=[VOCopts.resdir 'Segmentation/%s_%s_inst'];
VOCopts.seg.clsrespath=[VOCopts.seg.clsresdir '/%s.png'];
VOCopts.seg.instrespath=[VOCopts.seg.instresdir '/%s.png'];

VOCopts.layout.respath=[VOCopts.resdir 'Layout/%s_layout_' VOCopts.testset '.xml'];


fReport=fopen(report_fn,'a');
f_results=fopen([report_fn '.score'],'w');

try
    [accuracies,avacc,conf,rawcounts] = VOCevalseg(VOCopts,compid);   % compute and display PR    
    for i=1:VOCopts.nclasses
	cls=VOCopts.classes{i}
	fprintf(f_results,'%0.4f %s\n',accuracies(i),cls);
    end
    hasErrors=0;

catch 
    avacc=0;
    m=lasterror;
    fprintf(fReport,['Encountered error while evaluating segmentation:' m.message '\n']);
    hasErrors=1;
end
if hasErrors==0
   f_results_final=fopen([report_fn  '.final_score'],'w');
   fprintf(f_results_final,'%0.4f\n',avacc);
   fclose(f_results_final)
end
