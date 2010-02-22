# Software License Agreement (BSD License)
#
# Copyright (c) 2008, Willow Garage, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#  * Neither the name of Willow Garage, Inc. nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.


import threading

from django.conf import settings

import roslib; roslib.load_manifest('django_crowd_server')
import rospy

if settings.ROS_INTEGRATION:
    def init_ros(m):
        print "ROS init start"
        print m
        import roslib; roslib.load_manifest('django_crowd_server')
        import rospy

        rospy.init_node("django_crowd_server",disable_signals=True,anonymous=True)

        from annotation_publisher import PublishAnnotationNode
        m["sender"]=PublishAnnotationNode("annotation_publisher");
        print "ROS init done"
        
    ros_sender={"sender":None}
    t=threading.Thread(target=init_ros,args=(ros_sender,));
    t.start();
else:
    ros_sender={"sender":None}

def get_annotations_sender():
    return ros_sender["sender"];



def get_publishers():
    if get_annotations_sender() is None:
        return []
    return get_annotations_sender().get_publishers_info()



class ROSRPCException(Exception):
    pass
def _succeed(args):
    code, msg, val = args
    if code != 1:
        raise ROSRPCException("remote call failed: %s"%msg)
    return val

_caller_apis = {}
def get_api(master, caller_id):
    """
    Get XML-RPC API of node
    @param master: XML-RPC handle to ROS Master
    @type  master: xmlrpclib.ServerProxy
    @param caller_id: node name
    @type  caller_id: str
    @return: XML-RPC URI of node
    @rtype: str
    @raise ROSTopicIOException: if unable to communicate with master
    """
    caller_api = _caller_apis.get(caller_id, None)
    if not caller_api:
        try:
            code, msg, caller_api = master.lookupNode('/rostopic', caller_id)
        except socket.error:
            raise ROSRPCException("Unable to communicate with master!")
        if code != 1:
            caller_api = 'unknown address %s'%caller_id
        else:
            _caller_apis[caller_id] = caller_api
    return caller_api

def get_ros_topic_publishers(topic):
    #verbatim from rostopic

    publishers=[];

    def topic_type(t, pub_topics):
        matches = [t_type for t_name, t_type in pub_topics if t_name == t]
        if matches:
            return matches[0]
        return 'unknown type'

    master = roslib.scriptutil.get_master()
    try:
        state = _succeed(master.getSystemState('/rostopic'))

        pubs, subs, _ = state
        # filter based on topic
        subs = [x for x in subs if x[0] == topic]
        pubs = [x for x in pubs if x[0] == topic]

        pub_topics = _succeed(master.getPublishedTopics('/rostopic', '/'))
    except socket.error:
        raise ROSRPCException("Unable to communicate with master!")

    if not pubs and not subs:
        print >> sys.stderr, "Unknown topic %s"%topic
        return 1

    #print '-'*80
    topic_type_name=topic_type(topic, pub_topics)
    import itertools

    if pubs:
        print "Publishers: "
        for p in itertools.chain(*[l for x, l in pubs]):
            print " * %s (%s)"%(p, get_api(master, p))
            publishers.append({"node":p,"topic":topic,"topic_type":topic_type_name,"publisher_url":get_api(master, p)})
    else:
        print "Publishers: None"
    print ''

    if subs:
        print "Subscribers: "
        for p in itertools.chain(*[l for x, l in subs]):
            print " * %s (%s)"%(p, get_api(master, p))
    else:
        print "Subscribers: None"
    print ''

    return publishers



def on_submission(submission):
    if get_annotations_sender():
        try:
            print "Sending results"
            sender=get_annotations_sender()
            print "get xml"
            xml_str=submission.get_xml_str();
            print "get params"
            params=submission.hit.parse_parameters();
            print params
            if "ref_uid" in params:
                image_uid =str(params['ref_uid'])
            else:
                image_uid =str(params['frame'])

            uid = "submittedtask-%d" % submission.id;
            sender.send_annotation(xml_str,image_uid,submission.session.task_def.name,submission.session.code,uid)

        except Exception,e:
            print "Failed to send the anntoation message. ",e
