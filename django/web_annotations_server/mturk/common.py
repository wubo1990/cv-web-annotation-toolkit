
try:
    from boto.mturk.connection import MTurkConnection
    from boto.mturk.question import ExternalQuestion
    from boto.mturk.qualification import Qualifications, PercentAssignmentsApprovedRequirement,Requirement
    from boto.mturk.qualification_type import *
    hasBoto=True
except:
    hasBoto=False

class MTurkException(Exception):
     def __init__(self, rs):
         self.rs = rs
     def __str__(self):
         return str(self.rs)


def get_mt_connection(session):
    if session.sandbox:
        awshost='mechanicalturk.sandbox.amazonaws.com'
    else:
        awshost='mechanicalturk.amazonaws.com'

    conn = MTurkConnection(host=awshost,aws_secret_access_key=session.funding.secret_key,aws_access_key_id=session.funding.access_key)
    return conn
