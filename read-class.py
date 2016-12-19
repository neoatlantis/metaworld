#!/usr/bin/env python3
import os
import sys
from metaworld.mwclass import Classification

from tabulate import tabulate

try:
    dbpath = sys.argv[1]
    cid = int(sys.argv[2])
except:
    print("Open a classification: python mwclass.py <DatabasePath> <ClassID>")
    exit(1)

c = Classification(dbpath)
c.open(cid)

print("Classification name: %s" % c.name)
print("Following characteristics are defined:")
for qid in c.chars:
    question = c.questions[qid]
    print(" - %s %s:" % (question.category, question.name))
    for sa, at in c.chars[qid]:
        print("   * %s freq=%s" % (sa, at['freq']))
