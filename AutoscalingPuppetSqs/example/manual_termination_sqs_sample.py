#!/usr/bin/env python

import boto.sqs
from boto.sqs.message import RawMessage

aws_region = "sa-east-1"
sqs_queue = "autoscaling"
instance = "server1.example.com"
manual_termination = '{"Type" : "Notification", "Subject" : "Manual: termination for instance ' + instance + '", "Message" : "{\\"Event\\":\\"manual:EC2_INSTANCE_TERMINATE\\",\\"EC2InstanceId\\":\\"' + instance + '\\"}"}'

conn = boto.sqs.connect_to_region(aws_region)
q = conn.get_queue(sqs_queue)
q.set_message_class(RawMessage)
m = RawMessage()
m.set_body(manual_termination)
q.write(m)
