# Feed https://tcwg.ci.linaro.org/pluginManager/installed into this script
import sys

import lxml
import lxml.etree
import lxml.html
from lxml.cssselect import CSSSelector
from lxml.html import tostring

tree = lxml.html.parse(sys.argv[1])
root = tree.getroot()

def innerhtml(el):
    return ''.join([tostring(child) for child in el.iterchildren()])

for r in root.cssselect("table#plugins")[0].cssselect("tr"):
    tds = r.cssselect("td")
    if not tds:
        continue
    a = tds[2].getchildren()[0]
    plugin = a.get("href").split("/")[1]
    mark = ""
    if plugin in ("credentials", "ssh-credentials"):
        mark = "a"
    ver = a.text_content()
    print "    - %shttp://updates.jenkins-ci.org/download/plugins/%s/%s/%s.hpi" % (mark, plugin, ver, plugin)
