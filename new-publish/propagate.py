#!/usr/bin/env python
"""This script propagates build artifacts from build master host
to actual publishing location (snapshots)."""
import sys
import os
import optparse

import paramiko

import publib


# If this file exists, publishing will be to staging
STAGING_FLAG_FILE = "/etc/linaro/staging-publishing"
REMOTE_HOST_PRODUCTION = "snapshots.linaro.org"
REMOTE_HOST_STAGING = "staging.snapshots.linaro.org"
PUBLISH_USER_NAME = "linaro-android-build-publish"
TRIGGER_USER_NAME = "linaro-android-build-publish-trigger"
#PUBLISH_KEY_FILE = "/home/ubuntu/snapshots-sync2.new/linaro-android-build-publish"
#TRIGGER_KEY_FILE = "/home/ubuntu/snapshots-sync2.new/linaro-android-build-publish-trigger"
PUBLISH_KEY_FILE = "/var/lib/jenkins/.ssh/linaro-android-build-publish"
TRIGGER_KEY_FILE = "/var/lib/jenkins/.ssh/linaro-android-build-publish-trigger"
LOCAL_UPLOAD_DIR = "/mnt/publish/uploads"
REMOTE_UPLOAD_DIR = "/uploads/android"

def log(msg):
    print msg
    sys.stdout.flush()


if __name__ == "__main__":
    optparser = optparse.OptionParser(usage="%prog <job/build>")
    optparser.add_option("-s", "--staging", action="store_true", help="Publish to staging server")
    optparser.add_option("--identity-publish", metavar="KEY", default=PUBLISH_KEY_FILE, help="Publish SSH key file")
    optparser.add_option("--identity-trigger", metavar="KEY", default=TRIGGER_KEY_FILE, help="Trigger SSH key file")
    optparser.add_option("-n", "--dry-run", action="store_true", help="Don't actually publish files, log commands")
    optparser.add_option("--host", help="Override destination publishing host, for debugging")
    optparser.add_option("--step", default="all", help="Run only specific step")
    options, args = optparser.parse_args(sys.argv[1:])
    if len(args) != 1:
        optparser.error("Wrong number of arguments")

    publib.validate_build_id(args[0])

    print "Starting propagation phase"

    staging_flag = os.path.exists(STAGING_FLAG_FILE)

    if options.staging or staging_flag:
        remote_host = REMOTE_HOST_STAGING
        opt_staging = "-s"
    else:
        remote_host = REMOTE_HOST_PRODUCTION
        opt_staging = ""
    if options.host:
        remote_host = options.host

    print "Publishing to:", remote_host

    if options.step in ("all", "1"):
        file_list = []
        for root, dirs, files in os.walk(os.path.join(LOCAL_UPLOAD_DIR, args[0])):
            file_list.extend([os.path.join(root, f) for f in files])
        print "Files:", file_list
        strip = len(LOCAL_UPLOAD_DIR.strip("/").split("/"))
        dir_list = publib.make_dir_struct(file_list, REMOTE_UPLOAD_DIR, strip=strip)
        print "Dirs:", dir_list
        if not options.dry_run:
            log("Creating dir structure on upload server")
            publib.create_dir_struct(dir_list, remote_host, PUBLISH_USER_NAME,
                                      options.identity_publish)
            log("Done creating dir structure on upload server")
        upload_script = publib.make_upload_script(file_list, REMOTE_UPLOAD_DIR, strip=strip)
        log("Uploading files to upload server")
        publib.upload_files(upload_script, remote_host, PUBLISH_USER_NAME,
                             options.identity_publish, options)
        log("Done uploading files to upload server")

    if options.step in ("all", "2"):
        job, build = args[0].split("/")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(remote_host, username=TRIGGER_USER_NAME, key_filename=TRIGGER_KEY_FILE)
        log("Triggering moving of files from upload to download area")
        stdin, stdout, stderr = client.exec_command("reshuffle-files -t android -j %s -n %s -m %s" % (job, build, opt_staging))
        stdin.close()
        rc = stdout.channel.recv_exit_status()
        print "Moving phase completed with result: %d" % rc
        print "=== stdout ==="
        print stdout.read()
        print "=== stderr ==="
        print stderr.read()
        print "=============="
        client.close()
        sys.exit(rc)
