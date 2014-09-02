#!/bin/bash
#
# archive-slave-logs script may move not yet complete logs, so
# later new log with the same will be created (usually it has
# just one line though: "Connection terminated"). We copy with
# mv --backup, so original file will be backed up as *~. This
# script both such parts together (again, 2nd part usually
# contains just one line, but to be on safe side and fuly correct).
#
# This script should be run with sudo
#

cd /var/lib/jenkins/slave-logs

for f in 20*~; do
    main=`echo $f | sed -e 's/~//'`
    echo "cat $main >> $f && mv $f $main"
done
