import base64
import lxml.etree


def get_build_config(tree):
    tag = tree.xpath("/project/properties//defaultValue")
    assert len(tag) == 1
    tag = tag[0]
    d = {}
    for l in base64.decodestring(tag.text).split("\n"):
        l = l.strip()
        if not l or l[0] == "#":
            continue
        k, v = l.split("=", 1)
        d[k] = v
    return d


def add_or_replace_node(tree, node_xpath, node_text):
    new_node = lxml.etree.fromstring(node_text)
    nodes = tree.xpath(node_xpath)
    assert len(nodes) < 2, "Please use more selective XPath expression"
    if nodes:
        # First, add new node after existing
        nodes[0].addnext(new_node)
        # Then, delete the original node
        nodes[0].getparent().remove(nodes[0])
    else:
        parent_xpath, _ = node_xpath.rsplit("/", 1)
        parent = tree.xpath(parent_xpath)[0]
        parent.append(new_node)

def remove_node(tree, node):
    node.getparent().remove(node)

def add_child(tree, node_xpath, node_text):
    "Add new node (node_text) as last child of node_xpath."
    nodes = tree.xpath(node_xpath)
    assert len(nodes) == 1, "Found %d nodes with XPath %s, expected 1" % (len(nodes), node_xpath)
    new_node = lxml.etree.fromstring(node_text)
    nodes[0].append(new_node)


def add_sibling(tree, node_xpath, node_text):
    "Add new node (node_text) as next sibling after node_xpath."
    new_node = lxml.etree.fromstring(node_text)
    nodes = tree.xpath(node_xpath)
    assert len(nodes) > 0, "Node not found: %s" % node_xpath
    assert len(nodes) < 2, "Please use more selective XPath expression than %s" % node_xpath
    nodes[0].addnext(new_node)
