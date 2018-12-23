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
from io import StringIO, BytesIO
import xml.etree.ElementTree as ET
from lxml import etree

data_loc = 'data/Safari_Bookmarks_2018_12_22.html'
# -

# https://stackoverflow.com/questions/31543085/python-xml-handle-unclosed-token
parser = etree.XMLParser(recover=True, encoding='utf-8')
tree = etree.parse(StringIO(data_loc), parser)

print(len(parser.error_log))
error = parser.error_log[0]
print(error.message)
print(error.line)

print(StringIO(data_loc).getvalue())


