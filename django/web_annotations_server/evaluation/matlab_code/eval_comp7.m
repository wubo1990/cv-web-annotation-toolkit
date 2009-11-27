function eval_comp7(VOClocation,results_root,report_fn,compid)

% change this path if you install the VOC code elsewhere
if ~exist('compid','var')
   compid='comp7';
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

cls='layout';
try
    [recall,prec,ap]=VOCevallayout(VOCopts,compid,false);   % compute and display PR    
    fprintf(f_results,'%0.4f %s\n',ap,cls);
    hasErrors=0;
catch 
    ap=0;
    err=lasterror;
    fprintf(fReport,['Encountered error while evaluating class ' ...
                     '%s. AP 0 is used.' err.message '\n'],cls);
    fprintf(f_results,'%0.4f %s\n',ap,cls);
    hasErrors=1;
end

if hasErrors==0
  f_results_final=fopen([report_fn  '.final_score'],'w');
  fprintf(f_results_final,'%0.4f\n',ap);
  fclose(f_results_final);
end
