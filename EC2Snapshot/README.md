EC2Snapshot
-----------

Backup/Snapshot script for EBS volumes.  
You can specify volumes individually or in batch file.  

```bash
$ ./EC2Snapshot.py --help

USAGE
=====

./EC2Snapshot.py [-v|--volume] <volume> [-d|--description] <description> [-k|--keep] <number snapshots to keep>  
./EC2Snapshot.py [-b|--batch] <filename>  

Example: ./EC2Snapshot.py -v vol-ea30279b -d 'My Snapshot' -k 2  
Example: ./EC2Snapshot.py -b volumes.txt  

$ cat volumes.txt   
vol-a40b50cc,test snapshot,3  
vol-b10c20dd,another snapshot,3  

$ ./EC2Snapshot.py -b volumes.txt   
Deleting 1 from 3 Snapshots found for Volume vol-a40b50cc:  
...snap-900000d3 (test snapshot)  
Creating Snapshot for 'vol-a40b50cc'  
...snap-c0000887 (test snapshot)  
Deleting 0 from 0 Snapshots found for Volume vol-b10c20dd:  
Creating Snapshot for 'vol-b10c20dd'  
...snap-dcccccc9 (another snapshot)  
```
