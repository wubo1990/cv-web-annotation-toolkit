
try:
    raise Exception("NO ROS") 
    import roslib; roslib.load_manifest('mech_turk_ros') #django_crowd_server
    import rospy

    rospy.init_node("django_crowd_server",disable_signals=True,anonymous=True);

    from annotation_publisher import PublishAnnotationNode
    ros_sender=PublishAnnotationNode("annotation_publisher");

except Exception,e:
    print "Got exception:",e
    ros_sender=None


def get_annotations_sender():
    return ros_sender;



def get_publishers():
    if ros_sender is None:
        return []
    return get_annotations_sender().get_publishers_info()


def on_submission(submission):
    if ros_sender:
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
