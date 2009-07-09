from xml.dom import minidom


def xget(o,tagname):
	return o.getElementsByTagName(tagname);

def xget_child(o,tagname):
	for n in o.childNodes:
		if n.nodeName==tagname:
			return n
	return None;

def xget_v(o,tagname):
	try:
		fc=o.getElementsByTagName(tagname)[0].firstChild
		if fc:
			return	fc.nodeValue;
		else:	
			return None
	except:
		return None
def xget_v_dft(o,tagname,default):
	v=xget_v(o,tagname)
	if v is None:
		v=default
	return v
def xget_v3(o,tagname):
	fc=o.getElementsByTagName(tagname)[0].firstChild
	if fc:
		return	fc;
	else:	
		return None

def xget_v2(o,tagnames):
	return map(lambda t:xget_v(o,t),tagnames);

def xget_a(o,tagname):
	return o.attributes[tagname].value;
def xget_a2(o,tagnames):
	return map(lambda t:xget_a(o,t),tagnames);

def xadd(doc,x_parent,child_name,child_content):
	x_child = doc.createElement(child_name);
	x_child_c = doc.createTextNode(child_content)
	x_child.appendChild(x_child_c)
	x_parent.appendChild(x_child);

