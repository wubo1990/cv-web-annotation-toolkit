function interpret_results(ds_dir,prefix)

if isempty(ds_dir)
ds_dir='/var/django/web_annotations_server/packages/crowd_quality/test_data/pascal_bbox/results/ds2'
prefix='data.test'
end

dataset_fn=prefix;
predictions_fn=[prefix '.predictions'];

report_fn='test_report.txt'

ds=dlmread(fullfile(ds_dir,dataset_fn));
predictions=dlmread(fullfile(ds_dir,predictions_fn));

gt=ds(:,1);


plot(gt,'x')
hold on
plot(predictions,'yo')
hold off


th_low   = 0.75
th_high  = 0.9

correct_approval = sum((gt>=th_high) & (predictions>=th_low))
incorrect_rejections = sum((gt>=th_high) & (predictions<th_low))
correct_rejections = sum((gt<th_low) & (predictions<th_low))
incorrect_approval = sum((gt<th_low) & (predictions>th_low))

correct_usage = sum((gt>th_high) & (predictions>th_high))
incorrect_usage = sum((gt<th_high) & (predictions>th_high))

incorrect_dismissal = sum((gt>th_high) & (predictions<th_high))

rejection_error_rate=incorrect_rejections/(correct_approval+correct_rejections)
approval_error_rate=incorrect_approval/(correct_rejections+incorrect_rejections)

clean_data_error_rate=incorrect_usage/(correct_usage+incorrect_usage)
rejection_error_rate=incorrect_rejections/(correct_usage+incorrect_rejections)
waste_rate=incorrect_dismissal/sum(gt>th_high)
cost_overhead=sum(predictions>th_low)/correct_usage

fRpt=fopen(fullfile(ds_dir,report_fn),'w');
fprintf(fRpt,'clean_data_error_rate: %0.2f\n',clean_data_error_rate*100)
fprintf(fRpt,'rejection_error_rate: %0.2f\n',rejection_error_rate*100)
fprintf(fRpt,'waste_rate: %0.2f\n',waste_rate*100)
fprintf(fRpt,'cost_overhead: %0.2f\n',(cost_overhead-1)*100)
fclose(fRpt)