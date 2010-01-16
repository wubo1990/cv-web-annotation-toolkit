function answer = read_QA_problem_answer(task_root)


quality_fn=fullfile(task_root,'result_q.txt')
confidence_fn=fullfile(task_root,'result_c.txt')

quality=dlmread(quality_fn);
confidence=dlmread(confidence_fn);

answer=struct('quality',quality,...
	       'confidence',confidence);

	       