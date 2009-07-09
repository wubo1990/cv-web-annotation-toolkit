#!/usr/bin/env python

import urllib,zlib,array

segURL="http://vision-app1.cs.uiuc.edu:8080/datastore/load_segmentation/91385365F41F501FDA7F9A11E585489844DDBBB6/"
segURL="http://vision-app1.cs.uiuc.edu:8080/datastore/load_segmentation/0A2B43887A69C5E42B0B2F6CA6D9EC9D42C1C2D0/"

txt=urllib.urlopen(segURL).readline();

def txt2bin(txt):
    a=array.array('B')
    m={'A':0,'B':1,'C':2,'D':3,'E':4,'F':5,'G':6,'H':7,'I':8,'J':9,'K':10,'L':11,'M':12,'N':13,'O':14,'P':15};

    for i in range(0,len(txt),2):
        c=txt[i];
        c2=txt[i+1];
        v=m[c]*16+m[c2]
        a.append(v)
    return a;
binary_txt=txt2bin(txt);

t=zlib.decompress(binary_txt);

for v in t:
        print ord(v)
# (/ 584000 4 (* 400 365))


