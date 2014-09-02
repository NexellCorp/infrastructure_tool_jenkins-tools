#!/usr/bin/env python
import sys
import urllib2
import json
import time


URL = "https://android-build.linaro.org/jenkins/api/json"

f = urllib2.urlopen(URL)
server_info = json.load(f)
for job in server_info["jobs"]:
    f = urllib2.urlopen(job["url"] + "/api/json")
    job_info = json.load(f)
    for build in job_info["builds"]:
        f = urllib2.urlopen(build["url"] + "/api/json")
        build_info = json.load(f)
        tstamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(build_info["timestamp"] / 1000))
        print "%s,%s,%s" % (job["name"], build["number"], tstamp)
