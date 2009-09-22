# Create your views here.
from django.http import HttpResponse,Http404,HttpResponseRedirect
from django.shortcuts import render_to_response,get_object_or_404

import os
try:
	try:
		import Image
	except:
		from PIL import Image
except:	
	Image=None
import uuid

def main(request):
    return render_to_response('mturk_latex/input.html');

def compile(request):
    query=request.GET['query']
    
    print query

    id=uuid.uuid4();
    
    fn="/tmp/dj/%s.tex" % id
    hF=open(fn,'w')
    print >>hF,"""
    \\documentclass{article}
    \\begin{document}
    \\[
    """
    print >>hF,query
    print >>hF,"""
    \\]
    \\end{document}
    """
    hF.close();
    os.system("latex2html /tmp/dj/%s.tex" % id);
    #os.system("/tmp/dj/run.sh");

    return HttpResponse("<?xml version='1.0'?><eqn id='"+str(id)+"'></eqn>",mimetype="text/xml")



def getimg(request,id):
    image_filename="/tmp/dj/%s/img1.gif" % id;
    response = HttpResponse(mimetype="image/png")
    im = Image.open(image_filename);	    
    im.save(response, "PNG")
    return response
    return HttpResponse("MT Latex. Compile")
