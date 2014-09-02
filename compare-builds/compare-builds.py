import sys
import os

job = sys.argv[1]
build1 = sys.argv[2]
build2 = sys.argv[3]

def download(fname, build):
    base, ext = fname.split(".", 1)
    stamped_fname = "%s-%s.%s" % (base, build, ext)
    if os.path.exists(stamped_fname):
        print "Using cached %s" % stamped_fname
        return
    url_pat = "https://android-build.linaro.org/jenkins/job/linaro-android_staging-origen/%s/artifact/build/out/%s"
    url = url_pat % (build, fname)
    os.system("wget --no-check-certificate '%s' -O %s" % (url, stamped_fname))

def diff(fname, build1, build2):
    base, ext = fname.split(".", 1)
    cmdline = "diff -u %s-%s.%s %s-%s.%s > %s-%s-%s.diff" % (base, build1, ext,  base, build2, ext,  base, build1, build2)
    os.system(cmdline)


def compare_text_files(fname, build1, build2):
    download(fname, build1)
    download(fname, build2)
    diff(fname, build1, build2)

compare_text_files("source-manifest.xml", build1, build2)
compare_text_files("pinned-manifest.xml", build1, build2)
