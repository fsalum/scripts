#!/usr/bin/env python
# title          : ec2_launch.py
# date           : 20131216
# description    : Launch EC2 instances
# author         : Felipe Salum <fsalum@gmail.com>
#                :
# usage          : ec2_launch.py --help
# requirements   : Python Boto and credentials set in .boto config file or environment variables
# python_version : 2.6+
#
import sys
import boto
from boto.ec2 import regions
from optparse import OptionParser,OptionGroup
from time import sleep

def security_group_callback(option, opt, value, parser):
    setattr(parser.values, option.dest, value.split(','))

def options():
    description="Launch EC2 Instances with a few custom parameters"
    version="%prog 1.0"
    usage="%prog -n web01 -r us-east-1 -z us-east-1c -a ami-bba18dd2 -i c1.xlarge --disk_size=200 -k mykey -s 'Web Server,Config Client'"

    parser = OptionParser(usage=usage,version=version,description=description)
    group = OptionGroup(parser, "Default Options","Use default options if not specified")
    group.add_option("-r", "--region", dest="region", default="us-east-1", help="Region (default us-east-1)")
    group.add_option("-z", "--availability-zone", dest="availability_zone", default="us-east-1c", help="Availability Zone (default us-east-1c)")
    group.add_option("-a", "--ami", dest="ami", default="ami-bba18dd2", help="AMI ID (default to ami-bba18dd2)")
    group.add_option("-i", "--instance_type", dest="instance_type", default="c1.xlarge", help="Instance type (default to c1.xlarge)")
    group.add_option("-d", "--disk_size", dest="disk_size", default="200", help="EBS Root volume disk size (default to 200GB)")
    parser.add_option_group(group)

    group = OptionGroup(parser, "Mandatory Options","These options must be specified, no default values")
    group.add_option("-n", "--name", dest="name", default=None, help="Name tag for instance)")
    group.add_option("-k", "--key", dest="key", default=None, help="Key pair name)")
    group.add_option("-s", "--security_group", dest="security_group", default=None, type="string", action="callback", callback=security_group_callback, help="Security group names, separated by comma ('Web Server,DB Server,QA')")
    parser.add_option_group(group)

    (options, args) = parser.parse_args()

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)

    if not options.name or not options.key or not options.security_group:
        parser.error("Options -n (--name), -k (--key) and -s (--security_group) are mandatory.")

    return options.region,options.availability_zone,options.ami,options.instance_type,options.disk_size,options.name,options.key,options.security_group

def main():
    options.region,options.availability_zone,options.ami,options.instance_type,options.disk_size,options.name,options.key,options.security_group = options()

    # Connect the region
    for r in regions():
        if r.name == options.region:
            region = r
            break
    else:
        print "Region %s not found." % options.region
        sys.exit(1)

    ec2 = boto.connect_ec2(region=region)

    # Change the default ebs root volume size
    dev_sda1 = boto.ec2.blockdevicemapping.EBSBlockDeviceType(delete_on_termination=True)
    dev_sda1.size = options.disk_size # size in Gigabytes
    bdm = boto.ec2.blockdevicemapping.BlockDeviceMapping()
    bdm['/dev/sda1'] = dev_sda1

    reservation = ec2.run_instances(options.ami,
                                    placement=options.availability_zone,
                                    key_name=options.key,
                                    instance_type=options.instance_type,
                                    security_groups=options.security_group,
                                    block_device_map=bdm,
                                    user_data="""#!/bin/bash
                                    resize2fs /dev/sda1
                                    """,
                                    dry_run=True)

    instance = reservation.instances[0]

    print 'Waiting for instance to be running'
    while instance.state != 'running':
        print '.',
        sleep(5)
        instance.update()
    print 'done!'

    instance.add_tag("Name", value=options.name)

    print "Public IP: %s" % instance.ip_address
    print "Private IP: %s" % instance.private_ip_address

if __name__ == "__main__":
    main()
