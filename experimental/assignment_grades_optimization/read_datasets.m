function [all_subm,all_grades]=read_dataset(folder,session_ids)

all_subm=[];
all_grades=[];

for iS = 1:numel(session_ids)
  s=session_ids{iS}
  subm=dlmread(fullfile(folder,[s '.submissions.txt']));
  grades=dlmread(fullfile(folder,[s '.grades.txt']));
  all_subm=[all_subm subm'];
  all_grades=[all_grades grades'];
end