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

def parameters():
    description="Launch EC2 Instances with a few custom parameters"
    version="%prog 1.0"
    usage="%prog -n web01 -r us-east-1 -z us-east-1c -a ami-bba18dd2 -i c1.xlarge --disk_size=200 -k mykey -s 'Web Server,Config Client'"

    parser = OptionParser(usage=usage,version=version,description=description)
    group = OptionGroup(parser, "Default Options","Use default options if not specified")
    group.add_option("-a", "--ami", dest="ami", default="ami-bba18dd2", help="AMI ID (default to ami-bba18dd2)")
    group.add_option("-d", "--disk_size", dest="disk_size", default="200", help="EBS Root volume disk size (default to 200GB)")
    group.add_option("-e", "--environment", dest="environment", default="prod", help="Environment: prod,dev,qa,stg (default to prod)")
    group.add_option("-i", "--instance_type", dest="instance_type", default="m3.large", help="Instance type (default to m3.large)")
    group.add_option("-g", "--security_group", dest="security_group", default=None, type="string", action="callback", callback=security_group_callback, help="Security group names, separated by comma ('Web Server,DB Server,QA')")
    group.add_option("-G", "--security_group_ids", dest="security_group_ids", default=None, type="string", action="callback", callback=security_group_callback, help="Security group IDs, separated by comma ('sg-1a2b3c,sg-9z8y7x')")
    group.add_option("-p", "--iam_role", dest="iam_role", default=None, help="Instance Profile Name")
    group.add_option("-r", "--region", dest="region", default="sa-east-1", help="Region (default sa-east-1)")
    group.add_option("-s", "--subnet_id", dest="subnet_id", default=None, help="Subnet ID")
    group.add_option("-u", "--user_data", dest="user_data", default=None, help="User Data File")
    group.add_option("-z", "--availability-zone", dest="availability_zone", default="sa-east-1a", help="Availability Zone (default sa-east-1a)")
    group.add_option("--public_ip", dest="public_ip", action="store_true", default=False, help="Associate a Public IP")
    group.add_option("--dry-run", dest="dry_run", action="store_true", default=False, help="Dry run mode")
    parser.add_option_group(group)

    group = OptionGroup(parser, "Mandatory Options","These options must be specified, no default values")
    group.add_option("-n", "--name", dest="name", default=None, help="Name tag for instance)")
    group.add_option("-k", "--key", dest="key", default=None, help="Key pair name)")
    parser.add_option_group(group)

    (options, args) = parser.parse_args()

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)

    if not options.name or not options.key or not options.subnet_id:
        parser.error("Options -n (--name), -k (--key) and -s (--subnet_id) are mandatory.")

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

    instance = create_ec2(args,region,zonename)
    dns = create_route53(args,instance,zonename)

def create_route53(args,instance,zonename):
    fqdn = args.name + "." + zonename
    zone_dict = {}

    conn = boto.connect_route53()
    zone_id = conn.get_zone(zonename)

    zone_dict['id'] = zone_id.id
    zone = boto.route53.zone.Zone(conn, zone_dict)
    result = zone.add_a(fqdn,instance.private_ip_address)
    print "Adding %s to Route53: %s" % (fqdn,result)

def create_ec2(args,region,zonename):
    ec2 = boto.connect_ec2(region=region)

    # Change the default ebs root volume size
    root = '/dev/sda'
    dev_sda1 = boto.ec2.blockdevicemapping.EBSBlockDeviceType(delete_on_termination=True)
    dev_sda1.size = args.disk_size # size in Gigabytes
    bdm = boto.ec2.blockdevicemapping.BlockDeviceMapping()
    bdm[root] = dev_sda1

    # Assign public ip address on VPC
    if args.public_ip:
        interface = boto.ec2.networkinterface.NetworkInterfaceSpecification(subnet_id=args.subnet_id,
                                                                    groups=args.security_group_ids,
                                                                    associate_public_ip_address=True)
        interfaces = boto.ec2.networkinterface.NetworkInterfaceCollection(interface)
        args.subnet_id = None
        args.security_group_ids = None
    else:
        interfaces = None

    # Pulling user-data from external file if the parameter is passed
    user_data_content = ""
    if args.user_data is not None:
        with open(args.user_data, 'r') as f:
            user_data_content = f.read()
    user_data="""#!/bin/bash
HOSTNAME=%s
DOMAIN=%s
INTERNAL_IP=`curl http://169.254.169.254/latest/meta-data/local-ipv4`

# Rename host
sed -i "s/^HOSTNAME.*/HOSTNAME=$HOSTNAME/g" /etc/sysconfig/network
hostname $HOSTNAME
echo "$INTERNAL_IP $HOSTNAME.$DOMAIN $HOSTNAME" >> /etc/hosts

# Add user-data file content here
%s

# Run puppet
puppet agent --test --server puppet.sa-east-1.example.com --report true
"""% (args.name, zonename, user_data_content)

    reservation = ec2.run_instances(args.ami,
                                    placement=args.availability_zone,
                                    key_name=args.key,
                                    instance_type=args.instance_type,
                                    security_groups=args.security_group,
                                    block_device_map=bdm,
                                    user_data=user_data,
                                    instance_profile_name=args.iam_role,
                                    subnet_id=args.subnet_id,
                                    security_group_ids=args.security_group_ids,
                                    network_interfaces=interfaces,
                                    dry_run=args.dry_run)

    instance = reservation.instances[0]

    print 'Waiting for instance to be running'
    while instance.state != 'running':
        print '.',
        sleep(5)
        instance.update()
    print 'done!'

    instance.add_tag("Name", value=args.name)

    print "Name: %s" % args.name
    print "Instance ID: %s" % instance.id
    print "Public IP: %s" % instance.ip_address
    print "Private IP: %s" % instance.private_ip_address

    return instance

if __name__ == "__main__":
    main()
