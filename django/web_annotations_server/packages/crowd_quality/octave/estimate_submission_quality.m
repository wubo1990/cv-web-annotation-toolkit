function estimate_submission_quality(task_root)


problem=read_QA_problem(task_root);

agreement=problem.agreement;

quality_fn=fullfile(task_root,'result_q.txt')
confidence_fn=fullfile(task_root,'result_c.txt')

show_agreement_matrix(agreement);

num_submissions=max(size(agreement));
q_initial=ones(1,num_submissions);
c_initial=ones(1,num_submissions);

q=q_initial;
c=c_initial;
qc_prev=-1;

debug=1;
if debug
  answer=read_QA_problem_answer(task_root);
end

dampened_agreement=(agreement-0.5).*(agreement>0);

for iRound=1:100
  qc=q;
  delta=sum(abs(qc_prev-qc))
  if delta<0.01
    break
  end
  qc_prev=qc;

  q_unnormalized=agreement'*qc';
  %c_unnormalized=abs(agreement)*qc';
  q=sigmoid(q_unnormalized*3)';
  plot(q)
  hold on
  plot(problem.grades,'rx')
  plot(q.*sign(problem.grades-0.5),'bo')
  hold off

  if debug
    mean(q_unnormalized(problem.grades>=0.5))
    mean(q_unnormalized(problem.grades<0.5))
    mean(q(problem.grades>=0.5))
    mean(q(problem.grades<0.5))
  end

end

plot(q)
hold on
plot(c,'r')
hold off

fQ=fopen(quality_fn,'w')
fprintf(fQ,'%f\n',q);
fclose(fQ);
fC=fopen(confidence_fn,'w')
fprintf(fC,'%f\n',c);
fclose(fC);



function test
x=[-5:5];
plot(x,sigmoid(x-1))
plot(x,sigmoid(x))


task_root='/var/django/web_annotations_server/packages/crowd_quality/test_data/grouping_run1/problem1'


estimate_submission_quality(task_root)
evaluate_quality_estimate(task_root)


