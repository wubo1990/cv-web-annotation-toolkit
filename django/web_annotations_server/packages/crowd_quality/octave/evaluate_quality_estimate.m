function quality_report=evaluate_quality_estimate(task_root)


problem=read_QA_problem(task_root);

cut1=0.6;
cut2=0.6;

cut1b=0.8;
cut2b=0.8;

good=problem.grades>=cut1;
bad=problem.grades<cut1;

answer=read_QA_problem_answer(task_root);

plot(answer.quality)
hold on
plot(answer.confidence,'y')
plot(problem.grades,'r')
hold off

gt=good;
predictions=answer.quality>cut2;

good=sum(gt==predictions');
bad=sum(gt~=predictions');
err=bad/(good+bad)

results=evaluate_predictions_v2(answer.quality'-cut2,sign(problem.grades-cut1))

results=evaluate_predictions_v2(answer.quality'-cut2b,sign(problem.grades-cut1b))

h=hist(problem.grades)

roc=get_AP_from_ranking(answer.quality,sign(problem.grades-cut1))
roc2=get_AP_from_ranking(answer.quality,sign(problem.grades-0.9))

quality_report