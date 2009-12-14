#!/usr/bin/env bash

SRV=vch.cs.uiuc.edu:8080

for S in eval-1-box1 eval-1-box2 eval-1-box3 eval-1-box4; do
    wget -O $S.submissions.txt http://$SRV/mt/opt/$S/submissions/
    wget -O $S.grades.txt http://$SRV/mt/opt/$S/grades/
done