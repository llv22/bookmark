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
import shutil
from io import StringIO, BytesIO, IOBase
import xml.etree.ElementTree as ET
from lxml import etree

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
        assert os.path.exists(str)
        with open(fname, 'rb') as f:
            with line in f:
                raise NotImplementedError
        
    def newTree(self, root: TreeNode=None, f: IOBase):
        """
        new Tree and return root node of Tree via parsing input file handle f.
        """
        return root

root = TreeNode.newTreeNode({
    "type": TreeNodeType.FOLDED,
    "name": "Favoritess"
})
