#!/usr/bin/env python
# title          : elb_instances.py
# version        : 1.0
# date           : 20131202
# description    : List instances in ELB and show their Name tag in addition to Instance-id
# author         : Felipe Salum <fsalum@gmail.com>
#                :
# usage          : ./elb_instances.py -n elb-name
# requirements   : Python Boto and credentials set in .boto config file or environment variables
# python_version : 2.6+
#
import sys, getopt
import boto.ec2.elb, boto.ec2
from collections import defaultdict

def usage():
    print "\nUsage: %s -n elb-name" % sys.argv[0]
    print "Example: %s -n elb-fsalum-test\n" % sys.argv[0]

def options():
    global ElbName
    try:
        options,args = getopt.getopt(sys.argv[1:],'hn:', ['help','name='])
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)
    if not options:
        usage()
        sys.exit(2)

    for opt, arg in options:
        if opt in ('-h', '--help'):
            usage()
            sys.exit()
        if opt in ('-n', '--name'):
            ElbName = arg

def main():
    elbconn = boto.ec2.elb.connect_to_region('us-east-1')
    ec2conn = boto.ec2.connect_to_region("us-east-1")
    lb = elbconn.describe_instance_health(load_balancer_name=ElbName)
    describe = defaultdict(dict)

    for instances in lb:
        hostname = ec2conn.get_only_instances(instance_ids=instances.instance_id)
        describe[instances.instance_id]["instance_id"] = instances.instance_id
        describe[instances.instance_id]["hostname"] = hostname[0].__dict__['tags']['Name']
        describe[instances.instance_id]["state"] = instances.state
        describe[instances.instance_id]["description"] = instances.description

    for i in sorted(describe, key=lambda x: describe[x]['hostname']):
        print describe[i]['instance_id'], describe[i]['hostname'], "\t", describe[i]['state'], "\t", describe[i]['description']

if __name__ == "__main__":
    options()
    main()
