function l = loss_grading(q_i,q_j,u_j,g_i,g_j,g_ji)

diff=q_i(g_i)-q_j(g_j);
l=sum(u_j(g_j).*diff.*diff);

