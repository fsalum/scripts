# AWS Autoscaling cleanup on Puppet via SQS

This script reads messages from a SQS queue subscribed to a SNS topic used by your autoscaling groups.

You can also manually terminate non-autoscaling ec2 instances and send a message to the SQS queue for cleanup on puppet.

It will cleanup puppet certificates, deactivate node on PuppetDB and remove it from Puppet Dashboard.
Events:  
* autoscaling:EC2_INSTANCE_TERMINATE
* manual:EC2_INSTANCE_TERMINATE

# Pre-requisites

* Set up SNS notification for your autoscaling groups

```
aws autoscaling put-notification-configuration --auto-scaling-group-name <as group> --notification-types autoscaling:EC2_INSTANCE_LAUNCH autoscaling:EC2_INSTANCE_LAUNCH_ERROR autoscaling:EC2_INSTANCE_TERMINATE autoscaling:EC2_INSTANCE_TERMINATE_ERROR --topic-arn <SNS topic>
```

* Set up a SQS queue and subscribe it to your autoscaling SNS topic

* Attach a IAM policy to your IAM role or IAM user

```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "Stmt1401231621000",
      "Effect": "Allow",
      "Action": [
        "sqs:DeleteMessage",
        "sqs:ReceiveMessage"
      ],
      "Resource": [
        "arn:aws:sqs:sa-east-1:<AWS_ACCOUNT_ID>:<SQS_QUEUE_NAME>"
      ]
    }
  ]
}
``` 

* Use AWS instance-id as part of node hostname

* Install Boto and setup AWS Access/Secret keys or IAM Role on the machine


# Output sample

Use [example/autoscaling.msg](example/autoscaling.msg) as SQS message sample for testing the script.

The [example/manual_termination_sqs_sample.py](example/manual_termination_sqs_sample.py) script sends a 
`manual:EC2_INSTANCE_TERMINATE` event to the SQS queue so you can manually terminate non-autoscaling ec2 instances and cleanup them the same way.

```
[root@puppet1 ~]# ./puppet_sqs.py

instance: i-5be0fe4e
Cleaning up certificate for prod-app-admin-i-5be0fe4e.example.com

Notice: Revoked certificate with serial 65
Notice: Removing file Puppet::SSL::Certificate prod-app-admin-i-5be0fe4e.example.com at '/var/lib/puppet/ssl/ca/signed/prod-app-admin-i-5be0fe4e.example.com.pem'
prod-app-admin-i-5be0fe4e.example.com

Deactivating prod-app-admin-i-5be0fe4e.example.com on PuppetDB
Submitted 'deactivate node' for prod-app-admin-i-5be0fe4e.example.com with UUID d24f86b5-4eb8-4937-8079-8c21478b6fb7

Cleaning up dashboard for prod-app-admin-i-5be0fe4e.example.com

(in /root)

instance: server1.example.com
Hostname not found for server1.example.com

Removing not used message event autoscaling:EC2_INSTANCE_LAUNCH from queue
```
