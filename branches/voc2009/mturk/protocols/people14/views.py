# Create your views here.

from django.http import HttpResponse,Http404
from django.shortcuts import render_to_response

def showtask(request,protocol,session_code,task,workerId=None):
	if not protocol=="person14":
		raise Http404

	if task.dataset is None:
		img_base_url=None
	else:
		img_base_url=task.dataset.data_url

	submit_target="/mt/%s/%d/submit.html" % (session_code);
	if assignmentId in request.REQUEST:
		assignmentId=request.REQUEST['assignmentId'];
	elif workerId is not None:
		assignmentId=str(task.id);
	else: 
		assignmentId=None;

	return render_to_response('protocols/people14/task.html',
		 {'submit_target':submit_target, 
			'task': task, 
			'img_base_url':img_base_url,
			'workerId':workerId,
			'assignmentId':assignmentId})


def report_result(request,session_code):
    return HttpResponse("Report results")	

