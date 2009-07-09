function eval_comp1(VOClocation,results_root,report_fn,compid)

% change this path if you install the VOC code elsewhere
if ~exist('compid','var')
   compid='comp1';
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

% train and test classifier for each class
all_ap=zeros(1,VOCopts.nclasses);
for i=1:VOCopts.nclasses
    cls=VOCopts.classes{i}
    %if 0==0
    try
        [recall,prec,ap]=VOCevalcls(VOCopts,compid,cls,false);  % compute PR
        fprintf(f_results,'%0.4f %s\n',ap,cls);
        all_ap(i)=ap;
    catch 
        %else
        ap=0;
        m=lasterror;
        fprintf(fReport,['Encountered error while evaluating class ' ...
        '%s. AP 0 is used:' m.message'\n'],cls);
        fprintf(f_results,'%0.4f %s\n',ap,cls);
        all_ap(i)=ap;
    end
end

if ~all(all_ap==0)
   f_results_final=fopen([report_fn  '.final_score'],'w');
   fprintf(f_results_final,'%0.4f\n',mean(all_ap));
   fclose(f_results_final)
end
