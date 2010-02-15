

ds_dir='/var/django/web_annotations_server/packages/crowd_quality/test_data/pascal_bbox/results/ds3'
%ds_dir='/home/syrnick/inst/g-a-l/get-another-label-read-only/data/unittests'
prefix='data.all'
gold_fn=[prefix '.gold'];
predictions_fn=['pre-majority-vote.txt'];
predictions_fn=['post-majority-vote.txt'];




report_fn=[prefix 'test_report.txt'];

[gt_worker,gt_item,gt_value]=textread(fullfile(ds_dir,gold_fn),'%s %s %f')
[pred_item,pred_value]=textread(fullfile(ds_dir,predictions_fn),'%s %f');

[ign,gt2pred]=ismember(pred_item,gt_item);
assert(all(ign));

[ign,pred2gt]=ismember(gt_item,pred_item);
assert(all(ign));

correct=pred_value==gt_value(gt2pred);
wrong=pred_value~=gt_value(gt2pred);

num_correct=sum(correct)
num_wrong=sum(wrong)

