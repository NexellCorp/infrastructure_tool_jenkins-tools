#!/bin/sh
#
# Script to automate Jenkins config configuration backup to git.
# This mostly deals with job config backups - commit other changes
# manually (with good commit messages).
#
SSH_OPTS=""
# Auth proxy (-A) is mandatory for push access
SSH_AUTH="-A"
SSH="ssh $SSH_OPTS"

function usage () {
    echo "Usage: $0 <user> <host> status|diff|commit"
    exit 1
}

if [ $# -lt 3 ]; then
    usage
fi

HOST="$1@$2"
cmd=$3

set -x
if [ "$cmd" = "status" ]; then
    $SSH $HOST "cd /var/lib/jenkins; git status jobs"
elif [ "$cmd" = "status-all" ]; then
    $SSH $HOST "cd /var/lib/jenkins; git status"
elif [ "$cmd" = "diff" ]; then
    $SSH $HOST "cd /var/lib/jenkins; git diff jobs" | less
elif [ "$cmd" = "diff-all" ]; then
    $SSH $HOST "cd /var/lib/jenkins; git diff" | less
elif [ "$cmd" = "log" ]; then
    $SSH $HOST "cd /var/lib/jenkins; git log" | less
elif [ "$cmd" = "commit" ]; then
    msg="$4"
    if [ "$msg" = "" ]; then
        msg="Routine jobs update"
        $SSH $HOST "cd /var/lib/jenkins; git commit -m \"$msg\" jobs"
        msg="Capture new jobs"
        $SSH $HOST "cd /var/lib/jenkins; git add jobs; git commit -m \"$msg\" jobs"
    else
        $SSH $HOST "cd /var/lib/jenkins; git commit -m \"$msg\" jobs"
    fi
    echo "Jobs are now commited, but not pushed. Run $0 $1 $2 push"
elif [ "$cmd" = "push" ]; then
    gituser="$1"
    if [ "$4" != "" ]; then
        gituser="$4"
    fi
    $SSH $SSH_AUTH $HOST "cd /var/lib/jenkins; git push ssh://$gituser@linaro-private.git.linaro.org/srv/linaro-private.git.linaro.org/linaro-infrastructure/jenkins-config-$2.git master"
elif [ "$cmd" = "ssh" ]; then
    $SSH $SSH_AUTH $HOST
else
    usage
fi
