#!/usr/bin/env python
# title          : EC2Snapshot.py
# description    : Snapshot EC2 volumes and remove old snapshots.
# author         : Felipe Salum
# date           : 2013/02/21
# usage          : ./EC2Snapshot.py -h
# notes          : Install python-boto and add AWS credentials to your ~/.boto file
# python_version : 2.6+
#================================================================================================
import os
import getopt
import sys
import boto.ec2

def usage():
    print "\nUSAGE"
    print "=====\n"
    print "%s [-v|--volume] <volume> [-d|--description] <description> [-k|--keep] <number snapshots to keep>" % sys.argv[0]
    print "%s [-b|--batch] <filename>\n" % sys.argv[0]
    print "Example: %s -v vol-ea30279b -d 'My Snapshot' -k 2" % sys.argv[0]
    print "Example: %s -b volumes.txt\n" % sys.argv[0]

def batch(FileName):
    f = file(FileName,'r')
    for line in f:
        columns = line.split(',')
        VolumeId = columns[0]
        SnapshotDescription = columns[1]
        KeepSnaps = columns[2]
        delete(VolumeId,KeepSnaps)
        create(VolumeId,SnapshotDescription)

    sys.exit(0)

def delete(VolumeId,KeepSnaps):
    snapshots = conn.get_all_snapshots(filters={"volume-id": VolumeId})
    purge_list = sorted(snapshots, key=lambda each: each.start_time)[:-int(KeepSnaps)]
    totalSnaps = len(snapshots)
    totalPurge = len(snapshots)-int(KeepSnaps)
    if totalPurge < 0:
        totalPurge = 0
    print "Deleting %s from %s Snapshots found for Volume %s:" % (totalPurge,totalSnaps,VolumeId)
    for snaps_to_purge in purge_list:
        conn.delete_snapshot(snaps_to_purge.id)
        print "...%s (%s)" % (snaps_to_purge.id,snaps_to_purge.description)
    return

def create(VolumeId,SnapshotDescription):
    SnapshotId = conn.create_snapshot('%s' % (VolumeId), "%s" % (SnapshotDescription))
    print "Creating Snapshot for '%s'" % (VolumeId)
    print "...%s (%s)" % (str(SnapshotId)[9:],SnapshotDescription)
    return

def main():
    try:
        options, args = getopt.getopt(sys.argv[1:], 'hb:v:d:k:', ['help','batch=','volume=','description=','keep=',])
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)
    if not options:
        usage()
        sys.exit(2)

    VolumeId = None
    SnapshotDescription = None
    KeepSnaps = None
    FileName = None

    # Get Options
    for opt, arg in options:
        if opt in ('-h', '--help'):
            usage()
            sys.exit()
        if opt in ('-b', '--batch'):
            FileName = arg
        if opt in ('-v', '--volume'):
            VolumeId = arg
        elif opt in ('-d', '--description'):
            SnapshotDescription = arg
        elif opt in ('-k', '--keep'):
            KeepSnaps = arg

    # Create/Delete Snapshots
    if FileName:
        batch(FileName)
        sys.exit(0)
    if not SnapshotDescription and not KeepSnaps:
        print "ERROR: Please add a description to your Snapshot."
        sys.exit(2)
    elif SnapshotDescription and KeepSnaps:
        delete(VolumeId,KeepSnaps)
        create(VolumeId,SnapshotDescription)
    elif VolumeId and SnapshotDescription:
        create(VolumeId,SnapshotDescription)
    elif KeepSnaps:
        delete(VolumeId,KeepSnaps)
    else:
        usage()

if __name__ == "__main__":
    botocfg = "%s/.boto" % (os.path.expanduser('~'))
    if os.path.exists('%s' % (botocfg)):
        conn = boto.ec2.connect_to_region('us-east-1')
        main()
    else:
        print "Install python-boto and add your AWS credentials to %s" % (botocfg)
