function l = loss_for_opt(x)

global opt_ctx

q_i=x(opt_ctx.q_i_from:opt_ctx.q_i_to);
q_j=x(opt_ctx.q_j_from:opt_ctx.q_j_to);
u_j=x(opt_ctx.u_j_from:opt_ctx.u_j_to);


l=-loss_grading(q_i,q_j,u_j,opt_ctx.g_i,opt_ctx.g_j,opt_ctx.g_ji);

l=l+100000*(sum(x<0)+sum(x>1));
%q_i<0)+sum(q_j<0)+sum(q_i>1)+sum(q_j>1)+sum(u_j<0)+sum(u_j>1));

