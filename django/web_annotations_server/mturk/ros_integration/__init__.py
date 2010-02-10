
import roslib; roslib.load_manifest('mech_turk_ros') #django_crowd_server
import rospy

print "init"
rospy.init_node("django_crowd_server",disable_signals=True,anonymous=True);
print "init done"

"""
class RosConnector:
    __instance = None

    def __init__(self,name):
        self.sub_nodes={};

        self.rospy=rospy
        print "INIT NODE",name

        self.rospy.init_node(name,disable_signals=True,anonymous=True);


    def connect(name="crowd_django"):
        if RosConnector.__instance is None:
            RosConnector.__instance=RosConnector(name)
        return RosConnector.__instance
    connect=staticmethod(connect)
"""
try:
    #c=RosConnector.connect(name="annotation_sender")
    from annotation_publisher import PublishAnnotationNode
    ros_sender=PublishAnnotationNode(name);
except:
    ros_sender=None


def get_annotations_sender():
    return ros_sender;
    ros_connection = RosConnector.connect()
    name="annotation_sender"
    if name in ros_connection.sub_nodes:
        return ros_connection.sub_nodes[name]


    ros_connection.sub_nodes[name]=annotation_sender
    return annotation_sender


def get_publishers():
    if ros_sender is None:
        return []
    return get_annotations_sender().get_publishers_info()


def on_submission(submission):
    if ros_sender:
        try:
            print "Sending results"
            sender=get_annotation_sender()
            xml_str=submission.get_xml_str();
            params=submission.hit.parse_parameters();
            if "ref_uid" in params:
                uid = params['ref_time']
            else:
                uid = "submittedtask-%d" % submission.id;
                sender.send_annotation(xml_str,uid)

        except Exception:
            print "Failed to send the anntoation message. "
