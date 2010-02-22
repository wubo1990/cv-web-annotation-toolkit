import roslib; roslib.load_manifest('crowd_quality')

import generate_bbox_dataset
from cv_mech_turk2.tasks.boxes import get_bounding_boxes_from_xml_doc

def compute_agreement(x_submission,x_gold):
  example_boxes = get_bounding_boxes_from_xml_doc(x_submission);
  gold_boxes    = get_bounding_boxes_from_xml_doc(x_gold);    

  return generate_bbox_dataset.compute_bbox_set_agreement(example_boxes,gold_boxes)
