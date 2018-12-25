# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.3'
#       jupytext_version: 0.8.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
#   language_info:
#     codemirror_mode:
#       name: ipython
#       version: 3
#     file_extension: .py
#     mimetype: text/x-python
#     name: python
#     nbconvert_exporter: python
#     pygments_lexer: ipython3
#     version: 3.6.7
# ---

# +
import os
import re
import shutil
from io import StringIO, BytesIO, IOBase, TextIOBase
import xml.etree.ElementTree as ET
from lxml import etree
from IPython.display import display

data_loc = 'data/Safari_Bookmarks_2018_12_22.html'

# +
from enum import Enum

class TreeNodeType(Enum):
    FOLDED=1
    LINK=2

class TreeNode(object):
    """
    TreeNode for generic tree construction.
    """
    def __init__(self, _val: dict, _children: []=None):
        assert (_val is not None) and ("type" in _val) and ("name" in _val)
        self.val = _val
        self.children = []
        if _children:
            for child in _children:
                self.children.append(child)
                
    def appendChild(self, _child):
        if _child not in self.children:
            self.children.append(_child)
    
    @classmethod
    def newTreeNode(cls, _val: dict):
        return cls(_val)
# -

class Forest(object):
    """
    Forest constructed by list of parallel Tree from parsing html tree.
    """
    def __init__(self, fname: str):
        self.roots = []
        assert os.path.exists(fname)
        # check if end of f IOBase, record it first, then use for comparsion of closing
        with open(fname, 'rb') as f:
            # mark the end of stream, refer to https://stackoverflow.com/questions/10140281/how-to-find-out-whether-a-file-is-at-its-eof
            f.seek(-1, os.SEEK_END); self.eof = f.tell(); f.seek(0, os.SEEK_SET)
            while f.tell() != self.eof + 1:
                root = self.newTree(f)
                if root:
                    self.roots.append(root)
            
    def newTree(self, f: TextIOBase, level: int=0, parent: TreeNode=None):
        """[new Tree and return root node of Tree via parsing input file handle f.]
        Tips: 
            1. seek() and tell() to decide EOF
            2. DON'T return root, as in AAAAAAFAAA structure is difficult to return back, then insert
        Arguments:
            f [IOBase] - [input file handler]
            level [int] - [level in the current tree]
            parent [TreeNode] - [parent node of current treeNode, if exists, otherwise, it's None]
        """
        def findFirstDT(f: TextIOBase):
            """
            Need to handle with corner case: if can't find <DT>, as empty items for this group, need to stop immedidately.
                <DT><H3 FOLDED>lldb</H3>
                    <DL><p>
                    </DL><p>
            """
            fstart = f.tell()
            l = f.readline().decode('utf-8'); align = l.find('<')
            line = l.lstrip()
            while f.tell() != self.eof + 1 and line[:4] != '<DT>' and line[:5] != '</DL>':
                fstart = f.tell()
                l = f.readline().decode('utf-8'); align = l.find('<')
                line = l.lstrip()
            if line[:5] == '</DL>' or align == -1 or f.tell() == self.eof + 1 :
                # need to reset, as the starting item is empty for group
                if f.tell() != self.eof + 1:
                    f.seek(fstart, os.SEEK_SET)
                return None, None, None, False
            if line[:4] == '<DT>': 
                return line, align, fstart, True
        
        def findNextLineDT(f: TextIOBase):
            fstart = f.tell()
            line = f.readline().decode('utf-8'); align = line.find('<')
            line = line.lstrip()
            return line, align, fstart
        
        def createNode(content, f: TextIOBase, parent):
            # https://segmentfault.com/q/1010000000377077 to match tag
            m = re.search(r'(?<=<H3 FOLDED>)(.*?)(?=</H3>)', content)
            if m:
                # match for FOLDED node
                val = m.group(0)
                root = TreeNode.newTreeNode({
                    "type": TreeNodeType.FOLDED,
                    "name": val,
                    "level": level,
                })      
                # 1. read next line "<DL><p>"
                nextline = f.readline().decode('utf-8').strip()
                assert nextline == "<DL><p>"
                # 2. recursively process for tree node
                self.newTree(f, level+1, root)
                # 3. read end line "</DL><p>"
                endline = f.readline().decode('utf-8').strip()
                assert endline == "</DL><p>"
            else:
                m1 = re.search(r'(?<=<A HREF=)(.*?)(?=</A>)', content)
                if m1:
                    url, val = m1.group(0).split(">") 
                    # remove "" for url
                    url = url[1:-1]
                    root = TreeNode.newTreeNode({
                        "type": TreeNodeType.LINK,
                        "name": val,
                        "link": url,
                        "level": level,
                    })
                else:
                    raise ValueError("invalid tag for tree node")
            if parent:
                parent.appendChild(root)
            return root
        
        # find the first <DT> in tree structure for FOLDER or HREF
        l, align, fstart, existItem = findFirstDT(f)
        root = None
        if existItem:
            # only handle with item existing case
            content = l[4:]
            root = createNode(content, f, parent)

            nl, nalgin, nfstart = findNextLineDT(f)
            while (align == nalgin) and (nl[:4] == '<DT>'): 
                # if it's in the same level, already item for nextline
                content = nl[4:]
                createNode(content, f, parent)
                nl, nalgin, nfstart = findNextLineDT(f)
            else:
                # else if it's not in the same level, somehow need to rollback
                f.seek(nfstart, os.SEEK_SET)
        return root
                
    def preOrder(self):
        def preOrderTree(node: TreeNode):
            if node:
                if node.val["type"] == TreeNodeType.LINK:
                    if node.val["link"] not in self.conflict_dict:
                        self.conflict_dict[node.val["link"]] = 1
                    else:
                        self.conflict_dict[node.val["link"]] += 1
                        self.duplicate_total += 1
                    self.t += 1
                for child in node.children:
                    preOrderTree(child)
                  
        self.conflict_dict = {}; self.t = 0; self.duplicate_total = 0  
        for root in self.roots:
            preOrderTree(root)
            
        print("total url link: ", self.t)
        print("duplicate total url link: ", self.duplicate_total)
        duplicate_dict = {k:v for k, v in self.conflict_dict.items() if v > 1}
#         display("duplicate url links: ", duplicate_dict)
        print("max duplicate number of url link: ", max(duplicate_dict.values()))

forest = Forest(data_loc)
forest.preOrder()


