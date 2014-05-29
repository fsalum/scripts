#!/usr/bin/env python
#
# Based on Autoscaling notifications delete a hostname from
# PuppetDB, Puppet Dashboard and its certificate file
#

import json
import subprocess
import boto.sqs
from boto.sqs.message import RawMessage


def puppet_cleanup(instanceid):
    cmd = subprocess.Popen('puppet cert list --all | sed -ne \'/%s/s/.*"\([^"]*\)".*/\\1/p\'' % instanceid, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    hostname, cert_err = cmd.communicate()

    print "Cleaning up certificate for %s" % hostname
    cmd = subprocess.Popen('puppet node clean --unexport %s' % hostname, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    node_clean_output, node_clean_err = cmd.communicate()
    print node_clean_output

    print "Deactivating %s on PuppetDB" % hostname
    cmd = subprocess.Popen('puppet node deactivate %s' % hostname, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    node_deactivate_output, node_deactivate_err = cmd.communicate()
    print node_deactivate_output

    print "Cleaning up dashboard for %s" % hostname
    cmd = subprocess.Popen('rake RAILS_ENV=production -f /usr/share/puppet-dashboard/Rakefile node:del name=%s' % hostname, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    rake_output, rake_err = cmd.communicate()
    print rake_output
    return


def main():
    conn = boto.sqs.connect_to_region('sa-east-1')

    q = conn.get_queue('autoscaling')
    q.set_message_class(RawMessage)

    results = q.get_messages(num_messages=10, wait_time_seconds=20)

    if not len(results) == 0:
        for result in results:
            body = json.loads(result.get_body())
            msg = json.loads(body['Message'])
            event = msg['Event']
            asgroupname = msg['AutoScalingGroupName']
            instanceid = msg['EC2InstanceId']
            if event == 'autoscaling:EC2_INSTANCE_TERMINATE':
                puppet_cleanup(instanceid)
                q.delete_message(result)
            else:
                print "Removing not used message event %s from queue" % event
                q.delete_message(result)


if __name__ == "__main__":
    main()
