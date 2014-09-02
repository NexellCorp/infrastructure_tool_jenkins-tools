#!/usr/bin/env python
import sys
import os
import glob
import tempfile
import optparse

import paramiko


def validate_build_id(id):
    if "\\" in id:
        pass
    elif ".." in id:
        pass
    elif id[0] == "/":
        pass
    elif len(id.split("/")) != 2:
        pass
    else:
        return True

    print "Invalid build ID"
    sys.exit(1)


def get_file_list(patterns):
    expanded = []
    for p in patterns:
        for direl in glob.glob(p):
            if os.path.isfile(direl):
                expanded.append(direl)
    expanded.sort(lambda a, b: cmp(a.rsplit("/", 1), b.rsplit("/", 1)))
    return expanded

def common_path_prefix(s1, s2):
    "Find common prefix string of s1 & s2. Return (prefix, rest_of_s1)"
    s1 = s1.strip("/").split("/")
    s2 = s2.strip("/").split("/")
    if len(s1) > len(s2):
        l = len(s2)
    else:
        l = len(s1)
    for i in xrange(l):
        if s1[i] != s2[i]:
            return s1[:i], s1[i:]
    return s1[:l], s1[l:]

def strip_path_comps(path, num):
    path = path.strip("/")
    return "/".join(path.split("/")[num:])

def make_dir_struct(file_list, upload_dir, build_dir="", strip=0):
    script = []
    file_list = map(lambda f: strip_path_comps(f, strip), file_list)

    file_list = map(lambda f: os.path.join(build_dir, f), file_list)
    # Skip top-level files - dir for them is pre-existing
    file_list = filter(lambda f: "/" in f, file_list)
    dir_list = map(lambda f: os.path.dirname(f), file_list)
    dir_list = list(set(dir_list))
    dir_list.sort()
    prev_d = ''
    for d in dir_list:
        created, to_create = common_path_prefix(d, prev_d)
        p = os.path.join(upload_dir, "/".join(created))
        for comp in to_create:
            p = os.path.join(p, comp)
            script.append(p)
        prev_d = d
    return script

def create_dir_struct(dir_list, host, user, key):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=user, key_filename=key)
    sftp = paramiko.SFTPClient.from_transport(client.get_transport())
    for d in dir_list:
        try:
            sftp.listdir(d)
        except:
            sftp.mkdir(d, 0755)


def make_upload_script(file_list, upload_dir, build_dir="", strip=0):
    script = []
#    if dir and dir[0] != "/":
#        dir = "/" + dir
    last_dir = None
    for f in file_list:
        target_f = strip_path_comps(f, strip)
        # Prepend UPLOAD_DIR now, to avoid special case of no dir name
        # in file name
        target_f = os.path.join(upload_dir, build_dir, target_f)
        dirname, fname = target_f.rsplit("/", 1)
        if dirname != last_dir:
            script.append("cd %s" % dirname)
            last_dir = dirname
        script.append("put %s" % f)
    return script


def upload_files(upload_script, host, user, key, options):
    fd, fname = tempfile.mkstemp(prefix="sftp_script")
    os.close(fd)
    f = open(fname, "w")
    f.write("\n".join(upload_script) + "\n")
    f.close()

    cmd = "sftp -i %s -b %s %s@%s" % (key, fname, user, host)
    print cmd
    sys.stdout.flush()
    if not options.dry_run:
        rc = os.system(cmd)
        try:
            os.remove(fname)
        except:
            pass
        if rc != 0:
            print "ERROR: sftp transfer finished with error"
            sys.exit(1)
