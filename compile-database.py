#!/usr/bin/env python3

import os
import sys
import json

from metaworld.mwquestion import *
from metaworld.mwclass import *

"""
Compiles a given database into a large JSONP-alike script.
"""

try:
    dbpath = os.path.realpath(sys.argv[1])
except:
    print("python3 compile-database.py <DATABASE PATH>")

# print headings
print("""function loadMetaworldData(loadClass, loadQuestion){""")

# dump classifications

classesPath = os.path.join(dbpath, 'class')
classesList = os.listdir(classesPath)

def enumerateClass():
    global classesList
    for fn in classesList:
        if not fn.endswith('.yaml'): continue
        cid = int(fn.split('-')[0])
        c = Classification(dbpath)
        c.open(cid)
        yield c

for c in enumerateClass():
    cjson = json.dumps({
        'name': c.name,
        'chars': c.chars
    }, ensure_ascii=False)
    print("loadClass(%s);" % cjson)

# dump questions

questionPath = os.path.join(dbpath, 'question')
questionList = os.listdir(questionPath)

def enumerateQuestion():
    global questionList
    for fn in questionList:
        if not fn.endswith('.yaml'): continue
        qid = int(fn.split('-')[0])
        q = Question(dbpath)
        q.open(qid)
        yield q

for q in enumerateQuestion():
    print("loadQuestion(%s, %s);" % (
        json.dumps(q.getQuestionPresentation(), ensure_ascii=False),
        q.compileToJS()
    ))

print("""};""")
