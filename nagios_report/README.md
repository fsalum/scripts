nagios_report
=============

Reads the nagios log files and generate HTML reports/charts based on Google Visuzalition API

```bash
$ ./nagios_report.py --help

USAGE
=====

./nagios_report.py [-f|--file] <filename> [-a|--aggregated]

Example: ./nagios_report.py -f nagios1.log -f nagios2.log -a

```

HTML files are generated on /usr/share/nagios/reports  

