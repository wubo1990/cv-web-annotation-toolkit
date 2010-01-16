function problem = read_QA_problem(task_root)

agreement_fn=fullfile(task_root,'agreement.txt');
agreement_dta=dlmread(agreement_fn);
agreement=accumarray(agreement_dta(:,1:2)+1,agreement_dta(:,3));

ids_fn=fullfile(task_root,'submission_ids.txt');
final_grades_fn=fullfile(task_root,'final_grades.csv');

ids=dlmread(ids_fn);
grades_raw=dlmread(final_grades_fn);


[graded_submissions,grade_2_ids]=ismember(grades_raw(:,1),ids(:,2));
grades=zeros(size(ids,1),1);
grades(grade_2_ids(grade_2_ids>0))=grades_raw(grade_2_ids>0,2);

grade_table=[ 0 1 1 1 1 1 7 7 7 7 10 10 10 10 10]/10;
grades=grade_table(grades+1);

problem=struct('agreement',agreement,...
	       'ids',ids,...
	       'grades',grades);
	       