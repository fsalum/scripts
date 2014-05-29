{
  "Type" : "Notification",
  "MessageId" : "XYZ",
  "TopicArn" : "arn:aws:sns:sa-east-1:999999999999:autoscaling",
  "Subject" : "Auto Scaling: launch for group \"app-admin-asg\"",
  "Message" : "{\"StatusCode\":\"InProgress\",\"Service\":\"AWS Auto Scaling\",\"AutoScalingGroupName\":\"app-admin-asg\",\"Description\":\"Launching a new EC2 instance: i-5be0fe4e\",\"ActivityId\":\"8152bdac-2322-46fe-9ce2-c43a1aed6036\",\"Event\":\"autoscaling:EC2_INSTANCE_LAUNCH\",\"Details\":{\"Availability Zone\":\"sa-east-1b\"},\"AutoScalingGroupARN\":\"arn:aws:autoscaling:sa-east-1:999999999999:autoScalingGroup:XYZ:autoScalingGroupName/app-admin-asg\",\"Progress\":50,\"Time\":\"2014-05-28T02:53:04.399Z\",\"AccountId\":\"999999999999\",\"RequestId\":\"8152bdac-2322-46fe-9ce2-c43a1aed6036\",\"StatusMessage\":\"\",\"EndTime\":\"2014-05-28T02:53:04.399Z\",\"EC2InstanceId\":\"i-5be0fe4e\",\"StartTime\":\"2014-05-28T02:52:31.045Z\",\"Cause\":\"At 2014-05-28T02:52:15Z a user request update of AutoScalingGroup constraints to min: 1, max: 100, desired: 2 changing the desired capacity from 1 to 2.  At 2014-05-28T02:52:30Z an instance was started in response to a difference between desired and actual capacity, increasing the capacity from 1 to 2.\"}",
  "Timestamp" : "2014-05-28T02:53:04.476Z",
  "SignatureVersion" : "1",
  "Signature" : "XYZ",
  "SigningCertURL" : "XYZ",
  "UnsubscribeURL" : "XYZ"
}

{
  "Type" : "Notification",
  "MessageId" : "XYZ",
  "TopicArn" : "arn:aws:sns:sa-east-1:999999999999:autoscaling",
  "Subject" : "Auto Scaling: termination for group \"app-admin-asg\"",
  "Message" : "{\"StatusCode\":\"InProgress\",\"Service\":\"AWS Auto Scaling\",\"AutoScalingGroupName\":\"app-admin-asg\",\"Description\":\"Terminating EC2 instance: i-5be0fe4e\",\"ActivityId\":\"de7b133f-5824-4513-aade-de09d64b5462\",\"Event\":\"autoscaling:EC2_INSTANCE_TERMINATE\",\"Details\":{\"Availability Zone\":\"sa-east-1b\"},\"AutoScalingGroupARN\":\"arn:aws:autoscaling:sa-east-1:999999999999:autoScalingGroup:XYZ:autoScalingGroupName/app-admin-asg\",\"Progress\":50,\"Time\":\"2014-05-28T03:07:31.417Z\",\"AccountId\":\"999999999999\",\"RequestId\":\"de7b133f-5824-4513-aade-de09d64b5462\",\"StatusMessage\":\"\",\"EndTime\":\"2014-05-28T03:07:31.417Z\",\"EC2InstanceId\":\"i-5be0fe4e\",\"StartTime\":\"2014-05-28T03:06:34.921Z\",\"Cause\":\"At 2014-05-28T03:06:08Z a user request update of AutoScalingGroup constraints to min: 1, max: 100, desired: 1 changing the desired capacity from 2 to 1.  At 2014-05-28T03:06:34Z an instance was taken out of service in response to a difference between desired and actual capacity, shrinking the capacity from 2 to 1.  At 2014-05-28T03:06:34Z instance i-5be0fe4e was selected for termination.\"}",
  "Timestamp" : "2014-05-28T03:07:31.468Z",
  "SignatureVersion" : "1",
  "Signature" : "XYZ",
  "SigningCertURL" : "XYZ",
  "UnsubscribeURL" : "XYZ"
}
