#!/usr/bin/env python
# title          : nagios_report.py
# version        : 1.1
# date           : 20130320
# description    : Analyze nagios logs and generate report
# author         : Felipe Salum <fsalum@gmail.com>
# contributions  : Eduardo Saito
#                :
# usage          : ./nagios_report.py -f nagios1.log -f nagios2.log --agregated
# notes          : https://developers.google.com/chart/interactive/docs/gallery/columnchart
#                : https://developers.google.com/chart/interactive/docs/dev/gviz_api_lib
# python_version : 2.6+
#
# CHANGELOG:
#
# 1.0 - 2013/03/20
# First release
#
# 1.1 - 2013/05/06
# Moving to 'SERVICE NOTIFICATION' to filter by contact group
#
#================================================================================================
import getopt
import sys
import os
import re
import gviz_api

from datetime import datetime
from collections import defaultdict

def usage():
    print "\nUSAGE"
    print "=====\n"
    print "%s [-f|--file] <filename> [-a|--aggregated]\n" % sys.argv[0]
    print "Example: %s -f nagios1.log -f nagios2.log -a\n" % sys.argv[0]

def main():
    try:
        options, args = getopt.getopt(sys.argv[1:], 'hf:a', ['help','filename=','aggregated',])
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)
    if not options:
        usage()
        sys.exit(2)

    # Get Options
    FileList = []
    global ReportAggregated
    ReportAggregated = None

    for opt, arg in options:
        if opt in ('-h', '--help'):
            usage()
            sys.exit()
        if opt in ('-a', '--aggregated'):
            ReportAggregated = True
        if opt in ('-f', '--filename'):
            FileList.append(arg)

    if FileList:
        FileName = []
        agg_day,agg_hosts,agg_checks = defaultdict(int),defaultdict(int),defaultdict(int)
        try:
            for f in FileList:
                FileName = (open(f,'r'))
                # calculate individual tops
                top_day,top_hosts,top_checks = logfile(FileName)
                # print individual tops
                output(top_day,top_hosts,top_checks)
                # calculate aggregated tops
                agg_day,agg_hosts,agg_checks = global_counter(agg_day,agg_hosts,agg_checks,top_day,top_hosts,top_checks)
            if ReportAggregated is True:
                # print aggregated tops
                output_agg(agg_day,agg_hosts,agg_checks)
        except IOError as e:
            print 'Operation failed: %s' % e.strerror
            sys.exit(2)

def logfile(FileName):
    count_hosts,count_checks,count_day = defaultdict(int),defaultdict(int),defaultdict(int)
    top_day,top_hosts,top_checks = {},{},{}
    regex = re.compile('SERVICE NOTIFICATION: contactgroupname;.*;CRITICAL;')

    for line in FileName:
        servicealerts = regex.findall(line)
        for alerts in servicealerts:
            column = line.split(': ')
            # get timestamp
            t = column[0].strip('][SERVICE NOTIFICATION')
            timestamp = datetime.fromtimestamp(int(t))
            date = timestamp.strftime('%Y-%m-%d %H:%M:%S')
            day = timestamp.strftime('%Y-%m-%d')
            # get nagios fields
            fields = column[1].split(';')
            f_hostname, f_check, f_status, f_output = fields[1], fields[2], fields[3], fields[5]
            debug(date,day,f_hostname,f_check,f_status,f_output)
            # increment counters
            count_day[day] += 1
            count_hosts[f_hostname] += 1
            count_checks[f_check] += 1
            top_day[day] = count_day[day]
            top_hosts[f_hostname] = count_hosts[f_hostname]
            top_checks[f_check] = count_checks[f_check]
    return top_day,top_hosts,top_checks

def global_counter(agg_day,agg_hosts,agg_checks,top_day,top_hosts,top_checks):
    for k, v in sorted(top_day.items(), key=lambda x: x[1], reverse=True):
        agg_day[k] += top_day[k]
    for k, v in sorted(top_hosts.items(), key=lambda x: x[1], reverse=True):
        agg_hosts[k] += top_hosts[k]
    for k, v in sorted(top_checks.items(), key=lambda x: x[1], reverse=True):
        agg_checks[k] += top_checks[k]
    return agg_day,agg_hosts,agg_checks

def charts(description,data,column1,column2,column_order,chart_div,report_file):
    page_template = """
<html>
  <head>
    <!--Load the AJAX API-->
    <script type="text/javascript" src="https://www.google.com/jsapi"></script>
    <script type="text/javascript">

      // Load the Visualization API and the piechart package.
      google.load('visualization', '1.0', {'packages':['corechart']});

      // Set a callback to run when the Google Visualization API is loaded.
      google.setOnLoadCallback(drawChart);

      // Callback that creates and populates a data table,
      // instantiates the pie chart, passes in the data and
      // draws it.
      function drawChart() {

        // Create the data table.
        %(jscode)s

        // Set chart options
        var options = {
        'title':'%(chart_div)s',
        'width':1000, 'height':600,
        };

        // Instantiate and draw our chart, passing in some options.
        var chart = new google.visualization.ColumnChart(document.getElementById('%(chart_div)s'));

        %(aggregated)s

        chart.draw(jscode_data, options);
      }
    </script>
  </head>

  <body>
    <!--Div that will hold the pie chart-->
    <div id="%(chart_div)s"></div>
  </body>
</html>
"""
    # Loading it into gviz_api.DataTable
    report_dir = '/usr/share/nagios/reports'
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)
    output_html=open('%s/%s' % (report_dir,report_file), 'a+')
    data_table = gviz_api.DataTable(description)
    data_table.LoadData(data)

    aggregated = ''

    if ReportAggregated is True and ReportDaily is False:
        aggregated = """
        google.visualization.events.addListener(chart, 'select', function() {
        var selectionIdx = chart.getSelection()[0].row;
        var dateName = jscode_data.getValue(selectionIdx, 0);
        window.open('nagios_report_day_' + dateName + '.html');
        });
        """

    # Creating a JavaScript code string
    jscode = data_table.ToJSCode("jscode_data",)
                               #columns_order=(column1, column2),
                               #order_by=column_order)

    # Putting the JS code string into the template
    print >> output_html, page_template % vars()

def output(top_day,top_hosts,top_checks):
    max = 10
    global ReportDaily
    ReportDaily = True

    print "\nDAY"
    print "---"
    data_host, data_check = [], []
    d_list_host, d_list_check = [], []
    d_tuple_host, d_tuple_check = (), ()
    description_host, description_check = [], []
    desc_host, desc_check = (), ()
    for k, v in sorted(top_day.items(), key=lambda x: x[1], reverse=True):
        print "%s: %s" % (k,v)
        chart_date = k
        report_file = 'nagios_report_day_%s.html' % k
        d_tuple_host = k
        d_tuple_check = k
        desc_host = k
        desc_check = k
        d_list_host.append(d_tuple_host)
        d_list_check.append(d_tuple_check)
        description_host.append(desc_host)
        description_check.append(desc_check)

    print "\nTOP %s HOSTS" % max
    print "------------"
    for k, v in sorted(top_hosts.items(), key=lambda x: x[1], reverse=True)[:max]:
        print "%s: %s" % (k,v)
        d_tuple_host = v
        d_list_host.append(d_tuple_host)
        desc_host = (k,'number')
        description_host.append(desc_host)
    data_host.append(d_list_host)
    column1,column2,column_order,chart_div = top_day,"Hosts",top_day,"Hosts by Day - %s" % chart_date
    charts(description_host,data_host,column1,column2,column_order,chart_div,report_file)

    print "\nTOP %s ALERTS" % max
    print "-------------"
    for k, v in sorted(top_checks.items(), key=lambda x: x[1], reverse=True)[:max]:
        print "%s: %s" % (k,v)
        d_tuple_check = v
        d_list_check.append(d_tuple_check)
        desc_check = (k,'number')
        description_check.append(desc_check)
    data_check.append(d_list_check)
    column1,column2,column_order,chart_div = top_day,"Alerts",top_day,"Checks by Day - %s" % chart_date
    charts(description_check,data_check,column1,column2,column_order,chart_div,report_file)

def output_agg(agg_day,agg_hosts,agg_checks):
    max = 10
    global ReportDaily
    ReportDaily = False

    print "\nAGG DAY"
    print "-------"
    data = []
    for k, v in sorted(agg_day.items(), key=lambda x: x[0], reverse=False):
        print "%s: %s" % (k,v)
        data.append([k,v])
        report_file = 'nagios_report_weekly_%s.html' % k
    column1,column2,column_order,chart_div = "Date","Alerts","Date","Aggregated Days"
    description = [(column1),(column2,'number')]
    charts(description,data,column1,column2,column_order,chart_div,report_file)

    print "\nAGG %s HOSTS" % max
    print "------------"
    data = []
    for k, v in sorted(agg_hosts.items(), key=lambda x: x[1], reverse=True)[:max]:
        print "%s: %s" % (k,v)
        data.append([k,v])
    column1,column2,column_order,chart_div = "Host","Alerts","Alerts","Aggregated Hosts"
    description = [(column1),(column2,'number')]
    charts(description,data,column1,column2,column_order,chart_div,report_file)

    print "\nAGG %s ALERTS" % max
    print "-------------"
    data = []
    for k, v in sorted(agg_checks.items(), key=lambda x: x[1], reverse=True)[:max]:
        print "%s: %s" % (k,v)
        data.append([k,v])
    column1,column2,column_order,chart_div = "Checks","Alerts","Alerts","Aggregated Checks"
    description = [(column1),(column2,'number')]
    charts(description,data,column1,column2,column_order,chart_div,report_file)

def debug(date,day,f_hostname,f_check,f_status,f_output):
    #print date,day,f_hostname,f_check,f_status,f_output
    return

if __name__ == "__main__":
    main()
    print "\n"
