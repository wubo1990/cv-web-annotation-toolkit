# Create your views here.

import urllib

from django.http import HttpResponse
from django.shortcuts import render_to_response,get_object_or_404 

from models import *
import flickrapi

api_key = '931ed015f47760957ace73390eb3ac1d'

flickr = flickrapi.FlickrAPI(api_key)




def index(request):
    return render_to_response('image_collector/index.html');




def search_images(request):
    return render_to_response('image_collector/search.html');



	
def run_search(request):
    valid_licenses="4,2,1,5"
    numPerPage=20;
    search_query=request.REQUEST['query'];

    if not 'page' in request.REQUEST:
	page=1
    else:
	page=int(request.REQUEST['page']);

    src=ImageSource.objects.get(name='flickr');

    resp = flickr.photos_search(text=search_query, page=page, per_page=numPerPage,license=valid_licenses, 
			media='photo',extras='original_format,license,media,machine_tags')

    photos=resp.photos[0].photo;
    numPages=int(resp.photos[0].attrib['pages']);

    if page>1:
	prevPage=page-1;
    else:
 	prevPage=[];
    
    if page<numPages:
	nextPage=page+1;
    else:
	nextPage=[];

    page_list=range(1,numPages,10)

    query_ue=urllib.quote(search_query);
    for pic in photos:

	image,bCreated=Image.objects.get_or_create(source=src,source_image_id=pic.attrib['id']);
	if bCreated:
		image.url='http://flickr.com/photos/%s/%s' % (pic.attrib['owner'],pic.attrib['id']);
		image.preview_url='http://farm%s.static.flickr.com/%s/%s_%s_m.jpg' %(pic.attrib['farm'],pic.attrib['server'],pic.attrib['id'],pic.attrib['secret']);
		image.best_quality_url='http://farm%s.static.flickr.com/%s/%s_%s.jpg' %(pic.attrib['farm'],pic.attrib['server'],pic.attrib['id'],pic.attrib['secret']);
		image.save();
	if image.relevance>0:
		pic.html_class="ON"
	else:
		pic.html_class="OFF"

   
    return render_to_response('image_collector/results.html',
			{'photos':photos,
			 'query':query_ue,
			 'prevPage':prevPage,'nextPage':nextPage,'page':page,'totPages':numPages,'pagelist':page_list});




def mark_image(request,source,src_imgid,mark):

	#VERY basic - just tell that we got it.
	#return HttpResponse("%s %s %s"%(source,src_imgid,mark));

	src=ImageSource.objects.get(name=source);

	if mark=="ON":
		relevance=100;
	else:
		relevance=0;

	#Basic version - create and save the image	
	#image=Image(source=src,source_image_id=src_imgid,relevance=relevance);
	#image.save();

	#Advanced version - get one if exists, create new one if it doesn't
	image,bCreated=Image.objects.get_or_create(source=src,source_image_id=src_imgid);
	image.relevance=relevance
	image.save();

	if relevance>0:
		return HttpResponse("+")
	else:
		return HttpResponse("-")
	
def list_relevant(request):
	response = HttpResponse();
	for img in Image.objects.filter(relevance__gt=50):
		response.write("%s %s %s\n" % (img.source.name, img.source_image_id, img.best_quality_url));
	return response

def show_stats(request):
	stats=get_stats();
    	return render_to_response('image_collector/stats.html',
			{'stats':stats});

def get_full_image_info(request,source,src_imgid):

	src = get_object_or_404(ImageSource,name=source)
	img = get_object_or_404(Image,source=src,source_image_id=src_imgid)

	if source=="flickr":
	  try:
		resp = flickr.photos_getSizes(photo_id=src_imgid);

		max_size_item=filter(lambda n:n['label']=="Original",resp.sizes[0].size);
	
		if len(max_size_item)==0:
			max_size_item=resp.sizes[0].size[-1];
		else:
			max_size_item=max_size_item[-1];

		max_image_url=max_size_item['source'];
		max_display_url=max_size_item['url'];

		info = flickr.photos_getInfo(photo_id=src_imgid);

		photo= info.photo[0]
		license =  photo['license']
		realname = photo.owner[0]['realname']

		#url=photo.urls[0].url[0][0]
		url=filter(lambda n:n['type']=="photopage",photo.urls[0].url)[0].text;

		licenses={"0": {"name":"All Rights Reserved", url:""},
"4":{ "name":"Attribution License","url":"http://creativecommons.org/licenses/by/2.0/"},
"6":{ "name":"Attribution-NoDerivs License","url":"http://creativecommons.org/licenses/by-nd/2.0/"},
"3":{ "name":"Attribution-NonCommercial-NoDerivs License","url":"http://creativecommons.org/licenses/by-nc-nd/2.0/"},
"2":{ "name":"Attribution-NonCommercial License", "url":"http://creativecommons.org/licenses/by-nc/2.0/"},
"1":{ "name":"Attribution-NonCommercial-ShareAlike License", "url":"http://creativecommons.org/licenses/by-nc-sa/2.0/"},
"5":{ "name":"Attribution-ShareAlike License", "url":"http://creativecommons.org/licenses/by-sa/2.0/"},
}

		response = HttpResponse();
		response.write("%s\n" % src.name)
		response.write("%s\n" % img.source_image_id)
		response.write("%s\n" % max_image_url)
		response.write("%s\n" % url)
		response.write("%s\n" % license)
		response.write("%s\n" % licenses[license]['name'])
		response.write("%s\n" % licenses[license]['url'])
		response.write("%s\n" % realname)

		return response
 	  except:
		response = HttpResponse();
		response.write("%s\n" % src.name)
		response.write("%s\n" % img.source_image_id)
		response.write("NotFound\n") 
		return response

	return Http404();
"""
_query, page=page, per_page=numPerPage,license=valid_licenses, 
			media='photo',extras='original_format,license,media,machine_tags')

    photos=resp.photos[0].photo;
    numPages=int(resp.photos[0].attrib['pages']);

    if page>1:
	prevPage=page-1;
    else:
 	prevPage=[];
    
    if page<numPages:
	nextPage=page+1;
    else:
	nextPage=[];

    page_list=range(1,numPages,10)

    query_ue=urllib.quote(search_query);
    for pic in photos:

	image,bCreated=Image.objects.get_or_create(source=src,source_image_id=pic.attrib['id']);
	if bCreated:
		image.url='http://flickr.com/photos/%s/%s' % (pic.attrib['owner'],pic.attrib['id']);
		image.preview_url='http://farm%s.static.flickr.com/%s/%s_%s_m.jpg' %(pic.attrib['farm'],pic.attrib['server'],pic.attrib['id'],pic.attrib['secret']);
		image.best_quality_url='http://farm%s.static.flickr.com/%s/%s_%s.jpg' %(pic.attrib['farm'],pic.attrib['server'],pic.attrib['id'],pic.attrib['secret']);
		image.save();
	if image.relevance>0:
		pic.html_class="ON"
	else:

"""
