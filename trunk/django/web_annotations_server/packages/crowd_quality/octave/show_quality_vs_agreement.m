
problem = read_QA_problem(task_root);

h=hist(problem.grades,[0:0.1:1])
h/sum(h)

cut=0.5;
a1=problem.agreement(problem.grades>cut,problem.grades<cut);
a2=problem.agreement(problem.grades>cut,problem.grades>cut);
a3=problem.agreement(problem.grades<cut,problem.grades<cut);

v=problem.grades(problem.grades<cut)~=0;
show_agreement_matrix(a1)
show_agreement_matrix(a2)
show_agreement_matrix(a3)

a1_valid=(a1(a1~=0));
a2_valid=(a2(a2~=0));
a2_valid=(a2(a2~=0));
average_positive_to_negative_affinity=sum(a1_valid(a1_valid>0))./numel(a1_valid);
average_positive_to_positive_affinity=sum(a2_valid(a2_valid>0))./numel(a2_valid);
fprintf('Average positive to negative (bad) affinity is %0.3f\n',average_positive_to_negative_affinity);
fprintf('Average positive to positive (good) affinity is %0.3f\n',average_positive_to_positive_affinity);

all_to_good=problem.agreement(:,problem.grades>cut)';
good_to_all=problem.agreement(problem.grades>cut,:);
all_to_bad=problem.agreement(:,problem.grades<cut)';
bad_to_all=problem.agreement(problem.grades<cut,:);
mean(sum(good_to_all,2))
mean(sum(bad_to_all,2))
mean(sum(all_to_good,2))
mean(sum(all_to_bad,2))
