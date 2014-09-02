#!/usr/bin/env python

# Script copy old artifacts not present on snapshots.linaro.org from
# android-build.linaro.org like jenkins does via sftp and then moves
# to the desired destination using reshuffle-files command using ssh
# on snapshots.linaro.org
# Artifacts present on s.l.o are taken from list in builds-on-snapshots
# file.
# Command to generate artifacts list on s.l.o:
# find /srv3/snapshots.linaro.org/www/android/ -type d -maxdepth 3
# -mindepth 3 -wholename '*/~*/*' | sed
# 's/\/srv3\/snapshots\.linaro\.org\/www\/android\/~//'


import os
import glob
import re
import tempfile
import subprocess

from config import *

builds_list = []
remove_prefix = re.compile(remove)


def create_path_list(path, path_to_create):
    while len(path) > 0:
        path_to_create.insert(0, path)
        head, tail = os.path.split(path)
        if len(tail.strip()) == 0:  # Just in case path ends with a / or \
            path = head
            head, tail = os.path.split(path)
        path = head

    return path_to_create


def do_sftp_transfer(build, path_to_create, files):
    fd, fpath = tempfile.mkstemp()
    fnull = open(os.devnull, 'w')

    for path in path_to_create:
        os.write(fd, '-mkdir ' + remote_prefix + str(path) + '\n')
    for rfile in files:
        os.write(fd, '-put ' + str(rfile) + ' ' + remote_prefix +
                os.path.dirname(remove_prefix.sub('', str(rfile))) + '\n')
    os.close(fd)
    subprocess.call(["sftp", "-i", sync_key_file, "-q", "-r", "-b", fpath,
        "%s@%s" % (sync_user, host)], stdout = fnull, stderr = fnull)
    subprocess.call(["ssh", "-i", move_key_file, "%s@%s" % (move_user, host),
        move_cmd, build])

    fnull.close()
    os.remove(fpath)


def check_remote(job, build_number):
    global builds_list

    return "%s/%s" % (job, build_number) in builds_list


def load_build_list(fname):
    builds_list = []
    try:
        f = open(fname)
    except IOError:
        raise
    else:
        with f:
            while 1:
                line = f.readline()
                if not line:
                    break
                builds_list.append(line.replace("/", "_", 1).strip("\n"))

    return builds_list


def move_files(job):
    for dirname, dirnames, filenames in os.walk('%s/builds' % job):
        for build_number in dirnames:
            if os.path.islink(os.path.join(dirname, build_number)):
                build_started = "%s/%s" % (job, build_number)
                if check_remote(job, build_number):
                    print "Build skipped: " + build_started
                    continue
                files = []  # List of local files to be transferred
                remote_paths = []  # List of full remote paths to be created
                path_to_create = []  # List of subpaths of full paths
                print "Build started: " + build_started
                for src in source_files:
                    files.extend(glob.glob("%s/archive/%s" %
                        (os.path.join(dirname, build_number), src)))
                for rfile in files:
                    remote_paths.append(remove_prefix.sub('',
                        os.path.dirname(rfile)))
                uniq_remote_paths = list(set(remote_paths))
                for i in uniq_remote_paths:
                    path_to_create = create_path_list(i, path_to_create)
                do_sftp_transfer(build_started, path_to_create, files)


if __name__ == '__main__':
    builds_list = load_build_list("./builds-on-snapshots")
    cwd = os.getcwd()
    os.chdir(jobs_path)
    for ejob in jobs_list:
        jobs = glob.glob('%s*' % ejob)
        for job in jobs:
            move_files(job)
    os.chdir(cwd)
