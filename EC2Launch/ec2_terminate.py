#!/usr/bin/env python
# title          : ec2_terminate.py
# date           : 20140531
# description    : Terminate EC2 instances
# author         : Felipe Salum <fsalum@gmail.com>
#                :
# usage          : ec2_terminate.py --help
# requirements   : Python Boto and credentials set in .boto config file or environment variables
# python_version : 2.6+
#
import sys
import boto
import boto.sqs
from boto.ec2 import regions
from boto.sqs.message import RawMessage
from optparse import OptionParser, OptionGroup
from collections import defaultdict


def parameters():
    description = "Terminate EC2 Instances with a few custom parameters"
    version = "%prog 1.0"
    usage = "%prog -n web01 -r us-east-1"

    parser = OptionParser(usage=usage, version=version, description=description)
    group = OptionGroup(parser, "Default Options", "Use default options if not specified")
    group.add_option("-e", "--environment", dest="environment", default="prod", help="Environment: prod,dev,qa,stg (default to prod)")
    group.add_option("-r", "--region", dest="region", default="sa-east-1", help="Region (default sa-east-1)")
    group.add_option("--dry-run", dest="dry_run", action="store_true", default=False, help="Dry run mode")
    parser.add_option_group(group)

    group = OptionGroup(parser, "Mandatory Options", "These options must be specified, no default values")
    group.add_option("-n", "--name", dest="name", default=None, help="Name tag for instance)")
    parser.add_option_group(group)

    (options, args) = parser.parse_args()

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)

    if not options.name:
        parser.error("Option -n (--name) is mandatory.")

    return options


def main():
    args = parameters()

    # Connect the region
    for r in regions():
        if r.name == args.region:
            region = r
            break
    else:
        print "Region %s not found." % args.region
        sys.exit(1)

    if args.environment == 'prod':
        zonename = args.region + ".example.com"
    else:
        zonename = args.environment + "." + args.region + ".example.com"

    instance = terminate_ec2(args, region)
    remove_route53(args, zonename)
    notify_sqs(args,zonename)


def notify_sqs(args, zonename):
    sqs = boto.sqs.connect_to_region(args.region)

    instance = args.name + "." + zonename
    sqs_queue = "autoscaling"
    manual_termination = '{"Type" : "Notification", "Subject" : "Manual: termination for instance ' + instance + '", "Message" : "{\\"Event\\":\\"manual:EC2_INSTANCE_TERMINATE\\",\\"EC2InstanceId\\":\\"' + instance + '\\"}"}'

    q = sqs.get_queue(sqs_queue)
    q.set_message_class(RawMessage)
    m = RawMessage()
    m.set_body(manual_termination)
    q.write(m)
    print "SQS: Termination event sent for %s." % args.name


def remove_route53(args, zonename):
    fqdn = args.name + "." + zonename
    zone_dict = {}

    conn = boto.connect_route53()
    zone_id = conn.get_zone(zonename)

    zone_dict['id'] = zone_id.id
    zone = boto.route53.zone.Zone(conn, zone_dict)
    try:
        result = zone.delete_a(fqdn)
        print "Removed %s from Route53: %s" % (fqdn, result)
    except AttributeError:
        print "Route53: Hostname %s not found." % fqdn


def terminate_ec2(args, region):
    ec2 = boto.connect_ec2(region=region)
    ec2_data = defaultdict(dict)
    reservations = ec2.get_all_reservations()

    for reservation in reservations:
        instances = reservation.instances
        for instance in instances:
            if instance.__dict__['tags']['Name'] == args.name and instance.state == 'running':
                ec2_data[args.name]['instance_id'] = instance.id
                ec2_data[args.name]['private_ip'] = instance.private_ip_address
                ec2_data[args.name]['public_ip'] = instance.ip_address

                print "EC2: Instance %s terminated." % args.name
                ec2.terminate_instances(instance_ids=[ec2_data[args.name]['instance_id']], dry_run=args.dry_run)
                return ec2_data


if __name__ == "__main__":
    main()
