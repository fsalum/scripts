#!/usr/bin/env python
# title          : route53-cleanup.py
# date           : 20140101
# description    : Searches all Route53 entries and match with EC2 Public/Private IP addresses
#                : Return IP DNS records not found on EC2 instances to be cleaned
# author         : Felipe Salum <fsalum@gmail.com>
#                :
# usage          : route53-cleanup.py --help
# requirements   : Python Boto and credentials set in .boto config file or environment variables
# python_version : 2.6+
#

import sys
import argparse
import boto.ec2
from boto.ec2 import regions
from boto.route53.connection import Route53Connection
from boto.route53.exception import DNSServerError
from collections import defaultdict

description = 'Route53 Cleanup Reporter'
version = '%(prog)s 1.0'
usage = '%(prog)s --zoneid A2BCD3FGH4ZXYO'

def options():
    parser = argparse.ArgumentParser(usage=usage,description=description)
    parser.add_argument('-v', '--version', action='version', version=version)
    parser.add_argument('-r', '--region', dest='region', default='us-east-1', required=False, action='store', nargs='?', help='EC2 Region (Defaults: us-east-1)')
    group = parser.add_argument_group('required arguments')
    group.add_argument('-z', '--zoneid', dest='zoneid', default='None', required=True, action='store', nargs='?', help='Hosted Zone ID')
    args = parser.parse_args()
    return args

def get_ec2(args):
    ec2_ips = defaultdict(dict)

    # Connect the region
    for r in regions():
        if r.name == args.region:
            region = r
            break
    else:
        print "Region %s not found." % args.region
        sys.exit(1)

    print "Retrieving EC2 records..."
    conn = boto.connect_ec2(region=region)
    reservations = conn.get_all_reservations()

    for reservation in reservations:
        instances = reservation.instances
        for instance in instances:
            if instance.state == 'running':
                ec2_ips[instance.id]['private_ip'] = instance.private_ip_address
                ec2_ips[instance.id]['public_ip'] = instance.ip_address

    return ec2_ips

def get_route53(args):
    route53_ips = {}
    conn = Route53Connection()

    try:
        conn.get_hosted_zone(args.zoneid)
    except DNSServerError:
        print "%s zone not found" % args.zoneid
        sys.exit(1)

    #zonename = conn.get_hosted_zone(args.zoneid)
    #domain = zonename['GetHostedZoneResponse']['HostedZone']['Name']

    print "Retrieving Route53 records..."
    records = conn.get_all_rrsets(args.zoneid)

    for record in records:
        if record.type == 'A':
            route53_ips[record.name] = record.resource_records[0]

    return route53_ips

def main():
    args = options()
    route53_ips = get_route53(args)
    ec2_ips = get_ec2(args)
    report_ips = {}

    # Lookup Route53 IP on EC2
    for name,ip in route53_ips.items():
        match = 0
        for ec2_id in ec2_ips:
            if ip in ec2_ips[ec2_id].values():
                match = 1
        if match == 0:
            report_ips[name] = ip

    for name,ip in sorted(report_ips.items()):
        print "%s;%s" % (ip,name)

if __name__ == '__main__':
    main()
