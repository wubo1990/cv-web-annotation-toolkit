# Create your views here.

from django.http import HttpResponse,Http404
from django.conf import settings
import os

def save_segmentation(request,segmentation_id):
	print "Save segmentation"
	print segmentation_id;
	image=request.POST['V']
	print len(image)
	outF=open(os.path.join(settings.SEGMENTATION_ROOT,segmentation_id),'wb')
	outF.write(image);
	outF.close();

	return HttpResponse("Done")

def load_segmentation(request,segmentation_id):
	print "Load segmentation"
	print segmentation_id;
	filename=os.path.join(settings.SEGMENTATION_ROOT,segmentation_id);
	if not os.path.exists(filename):
		raise Http404

	outF=open(filename,'rb');
	content=outF.read();
	outF.close();
	print content
	return HttpResponse(content,mimetype="text/plain")