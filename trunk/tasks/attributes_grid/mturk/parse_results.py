#!/usr/bin/env python
import os,sys,time,urllib,random,re,yaml

if len(sys.argv)<2:
	print """Usage: ./parse_results.py output_root
E.g. ./parse_resutls.py runs/sandbox1
"""
	sys.exit();


FN="workload.results";

OUTD=sys.argv[1];
if not OUTD[-1] == '/':
	OUTD=OUTD+'/';

OUTDPRIVATE=OUTD+"results_private/";
OUTD=OUTD+"results/";

if not os.path.exists(OUTD):
	os.makedirs(OUTD)

if not os.path.exists(OUTDPRIVATE):
	os.makedirs(OUTDPRIVATE)

lines=file(FN,'r').readlines();
header=lines[0];
attr_names=map(lambda s:s.strip("\"\n"),header.split("\t"));

workersFN="%s/workers.txt" % (OUTDPRIVATE)	
fWorkers=open(workersFN,'w');

commentsFN="%scomments.txt"%(OUTD)
fComments=open(commentsFN,'w');

resultsFN="%sall_attributes.txt"%(OUTD)
fResults=open(resultsFN,'w');

fields=map(lambda s:s.strip('"'),lines[0].strip("\n").split("\t"));


nToGrade=0;
iAlignmentSqn=0;

attribute_re=re.compile("Answer.A_obj(?P<itemId>[^_]+)_(?P<attribute>.*)");
attributes={};

for (iLine,l) in enumerate(lines[1:]):
	values=map(lambda s:s.strip("\"\n"),l.split("\t"));

	vMap={};
	for (iV,v) in enumerate(values):
		vMap[fields[iV]]=v;

	if not "Answer.Comments" in vMap:
		continue;

	assignmentId=vMap["assignmentid"];
	for (iV,v) in enumerate(values):
		if v=="":
			continue
		match_result=attribute_re.match(fields[iV]);
		if match_result:
			item=match_result.group('itemId');
			attribute=match_result.group('attribute');
			print item,attribute,v
			if item not in attributes:
				attributes[item]={};
			item_dict=attributes[item]
			if assignmentId not in item_dict:
				item_dict[assignmentId]={};
			item_assignment_dict=item_dict[assignmentId];
			item_assignment_dict[attribute]=v;
	
	comments=vMap["Answer.Comments"];

	if not comments=="":
		print >>fComments,comments
		print comments

	continue

yaml.dump(attributes,fResults)
fResults.close();
fComments.close();
	
