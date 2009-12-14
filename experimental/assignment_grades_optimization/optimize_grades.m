folder='~/projects/cv-web-annotation-toolkit/experimental/assignment_grades_optimization/dataset1/';
session_ids={'eval-1-box1','eval-1-box2','eval-1-box3','eval-1-box4'};

[all_subm,all_grades]=read_datasets(folder,session_ids)
idx_grade=3
idx_submission=1;
idx_grading_submission=2;

plot(sort(all_grades(3,:)))
sum(all_grades(3,:)<10)
title('All grades')


%% Expert grades
expert_grades=all_grades(6,:)==100
sum(expert_grades)

[h_expert,xx]=hist(all_grades(idx_grade,expert_grades))
grade_distribution_expert=h_expert/sum(h)

bar(xx,h_expert)
bar(xx,grade_distribution_expert)


%% Non-expert grades
[h_non_expert,xx]=hist(all_grades(idx_grade,~expert_grades))
grade_distribution_non_expert=h_non_expert/sum(h_non_expert)
bar(xx,h_non_expert)
bar(xx,grade_distribution_non_expert)


%% Non-expert to expert KL-divergence
kl_d=grade_distribution_non_expert.*log(grade_distribution_non_expert ./ (grade_distribution_expert+(grade_distribution_expert==0)) + (grade_distribution_non_expert<1e-5))
kl_divergence=sum(kl_d)



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

CostPayment = -0.02;
CostError   = -3*CostPayment;
Utility     = 0.05;
CostFailure = -0.03;


num_submissions=size(all_subm,2)
num_expert_grades=sum(expert_grades)
num_non_expert_grades=sum(~expert_grades)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%Remap quality metrics

grades_only=all_grades(idx_grade,~expert_grades);
g_ji=0*(grades_only==3) + 0.5*(grades_only==7)+ 1*(grades_only>=10);
g_i_id=all_grades(idx_submission,~expert_grades);
[ign,g_i]=ismember(g_i_id,all_subm(1,:));
g_j=all_grades(idx_grading_submission,~expert_grades);
unique_grading_submissions=unique(g_j);
[ign,g_j]=ismember(g_j,unique_grading_submissions);
g_ij_sp=sparse(g_i,g_j,g_ji);


%Initialization
q_j=rand(1,numel(unique_grading_submissions));
q_i=rand(1,num_submissions);
u_j=q_j*0+1; %Use all grading submissions

%Grading mismatch loss
diff=q_i(g_i)-q_j(g_j);
sum(diff.*diff)

%Grading 



l_g=loss_grading(q_i,q_j,u_j,g_i,g_j,g_ji)

global opt_ctx
opt_ctx=struct('q_i_from',1,...
	       'q_i_to',numel(q_i),...
	       'q_j_from',numel(q_i)+1,...
	       'q_j_to',numel(q_i)+numel(q_j),...
	       'u_j_from',numel(q_i)+numel(q_j)+1,...
	       'u_j_to',numel(q_i)+numel(q_j)+numel(u_j),...
	       'g_i',g_i,...
	       'g_j',g_j,...
	       'g_ji',g_ji);
	
x0=[];       
x0(1:numel(q_i))=q_i;
x0(numel(q_i)+1:numel(q_i)+numel(q_j))=q_j;
x0(numel(q_i)+numel(q_j)+1:numel(q_i)+numel(q_j)+numel(u_j))=u_j;

l = loss_for_opt(x0)

opts=optimset('MaxIter',1000);
x=fminunc(@loss_for_opt,x0,opts);

l = loss_for_opt(x)

