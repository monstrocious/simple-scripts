#!/bin/bash


#Author: Mohamed Ibrahim


#The biggest disadvantages of OpenSSH is that, you cannot execute same command on multiple hosts at one go and OpenSSH is not developed to perform such tasks. 
#This is where Parallel SSH or PSSH tool comes in handy, is a python based application, which allows you to execute commands on multiple hosts in parallel at the same time.

#http://freshmeat.sourceforge.net/projects/pssh/


#Pssh package includes the following:

#pssh – is a program for running ssh in parallel on a multiple remote hosts.
#pscp – is a program for copying files in parallel to a number of hosts.
#Pscp – Copy/Transfer Files Two or More Remote Linux Servers
#prsync – is a program for efficiently copying files to multiple hosts in parallel.
#pnuke – kills processes on multiple remote hosts in parallel.
#pslurp – copies files from multiple remote hosts to a central host in parallel.


#Install pssh:
#yum install python-pip
#pip install pssh


#awsls is my host ec2 gather information located in this same directory.
#Find up-to-date instance IP's and store them in a file with :22 after the IPaddress
#:22 is needed for pssh to know to ssh via port 22
awsls | grep "running" | awk  '{print $5}' |grep -v "None" > current_hosts     
sed 's/$/:22/' current_hosts > pssh_hosts


#For Amazon linux instances
pssh -x '-t -t' -i -h pssh_hosts -l ec2-user "$1"

#For Ubuntu instances
pssh -x '-t -t' -i -h pssh_hosts -l ubuntu "$1"




#example command   ./parallel_ssh.sh "uptime"
