#!/usr/bin/env python
import sys
import os
import re
import datetime
import optparse


JOBS_ROOT = "/var/lib/jenkins/jobs/"

# TODO: move this into separate "script" file, allow to pass such script
# to execute by the main processor
PARSE = [
{"re": r"curl.+/seed/", "capture": "seed_url", "state": "SEED_DL"},
{"if": "SEED_DL", "re": "^real\t(?P<seed_dl_time>.+)", "state": ""},

{"re": "^Checking out files", "state": "REPO_CO"},
{"if": "REPO_CO", "re": "^real\t(?P<repo_co_time>.+)", "state": "END"},
]

def parse_time_time(s):
    m = re.match(r"(.+)m(.+)s", s)
    return datetime.timedelta(minutes=int(m.group(1)), seconds=float(m.group(2)))

def PROCESS(captures):
    if "seed_dl_time" not in captures or "repo_co_time" not in captures:
        return False
    captures["seed_dl_time"] = parse_time_time(captures["seed_dl_time"])
    captures["repo_co_time"] = parse_time_time(captures["repo_co_time"])
    captures["total_co_time"] = captures["seed_dl_time"] + captures["repo_co_time"]

REPORT2 = """\
Download time: %(seed_dl_time)s
Checkout time: %(repo_co_time)s
Total time   : %(total_co_time)s
"""
REPORT = """\
%(job_name)s, %(build_no)s, %(seed_dl_time)s, %(repo_co_time)s, %(total_co_time)s
"""

#+ curl --silent --show-error http://android-build.linaro.org/seed/pandaboard.mirror.tar.gz
#+ gzip -d -c
#+ tar x

#real<-->1m50.108s

class FinishProcessing:
    pass

def process_file(fname, captures):
    f = open(fname)
    state = ""

    try:
        for l in f:
            for rule in PARSE:
                if "if" not in rule or rule["if"] == state:
                    m = rule["re"].search(l)
                    if m:
                        captures.update(m.groupdict())
                        if "state" in rule:
                            state = rule["state"]
                            if state == "END":
                                raise FinishProcessing
    except FinishProcessing:
        pass

    if PROCESS(captures) == False:
        return None
    return REPORT % captures


def get_build_no(build_path):
    f = open(build_path + "/build.xml")
    for l in f:
        if "<number>" in l:
            f.close()
            return re.search(r"[0-9]+", l).group(0)
    f.close()


def process_one_log(fname, job_name, build_no):
        captures = {"job_name": job_name, "build_no": build_no}
        report = process_file(fname, captures)
        if report:
            sys.stdout.write(report)

optparser = optparse.OptionParser(usage="%prog")
optparser.add_option("--pattern", help="Process only jobs matching regex pattern")
optparser.add_option("--file", help="Process one log")
options, args = optparser.parse_args(sys.argv[1:])
if len(args) != 0:
    optparser.error("Wrong number of arguments")


# Precompile regexes
for rule in PARSE:
    rule["re"] = re.compile(rule["re"])

if options.file:
    process_one_log(options.file, "unknown-job", "unknown-build")
    sys.exit()

for path, dirs, files in os.walk(JOBS_ROOT):
    if "log" in files:
        if "build.xml" not in files:
            continue
        job_name = path[len(JOBS_ROOT):].split("/", 1)[0]
        if options.pattern and not re.search(options.pattern, job_name):
            continue
        build_no = get_build_no(path)
        process_one_log(path + "/log", job_name, build_no)
