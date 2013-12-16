EC2Launch
-----------

Launch EC2 instances (EBS based AMI) with custom root volume size.  

```bash
$ ./ec2_launch.py --help

Usage: ec2_launch.py -n web01 -r us-east-1 -z us-east-1c -a ami-bba18dd2 -i c1.xlarge --disk_size=200 -k mykey -s 'Web Server,Config Client'  

Launch EC2 Instances with a few custom parameters  

Options:  
  --version             show program's version number and exit  
  -h, --help            show this help message and exit  

  Default Options:  
    Use default options if not specified  

    -r REGION, --region=REGION  
                        Region (default us-east-1)  
    -z AVAILABILITY_ZONE, --availability-zone=AVAILABILITY_ZONE  
                        Availability Zone (default us-east-1c)  
    -a AMI, --ami=AMI   AMI ID (default to ami-bba18dd2)  
    -i INSTANCE_TYPE, --instance_type=INSTANCE_TYPE  
                        Instance type (default to c1.xlarge)  
    -d DISK_SIZE, --disk_size=DISK_SIZE  
                        EBS Root volume disk size (default to 200GB)  

  Mandatory Options:  
    These options must be specified, no default values  

    -n NAME, --name=NAME  
                        Name tag for instance)  
    -k KEY, --key=KEY   Key pair name)  
    -s SECURITY_GROUP, --security_group=SECURITY_GROUP  
                        Security group names, separated by comma ('Web  
                        Server,DB Server,QA')  
```
