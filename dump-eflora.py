#!/usr/bin/env python3

import json
import os
import sys
import re

from metaworld.classification import newClassification

##############################################################################
# Determine input and output parameters
try:
    inputpath = sys.argv[1]
    outputpath = sys.argv[2]
except Exception:
    print("python dump-eflora.py <JSON> <DATABASE PATH>")
    exit(1)
##############################################################################
# Sort out json data from items.eflora.cn

src = open(inputpath, 'r').read().strip()

for each in ["type", "jiange", "txt", "to", "name"]:
    src = src.replace('%s:' % each, '"%s":' % each)

if src.endswith(';'):
    src = src[:-1]


j = json.loads(src)

items = []

def getname(i):
    name = re.search('>(.+)<', i)
    if name:
        return name.group(1)
    return None

for each in j:
    items.append({
        'id': each['type'],
        'desc': each['txt'],
        'next': each['to'],
        'result': getname(each['name']),
    })

##############################################################################
# sort items into a numbered list -> frps

frps = {}
for item in items:
    entryID = item['id']
    if not entryID in frps: frps[entryID] = []
    frps[entryID].append({
        'desc': item['desc'],
        'next': item['next'],
        'prev': None,
        'result': item['result'],
    })

for questionID in frps:
    for answerID in range(0, len(frps[questionID])):
        nextID = frps[questionID][answerID]['next']
        if nextID < 0: continue
        for nextAnswerID in range(0, len(frps[nextID])):
            if None != frps[nextID][nextAnswerID]['prev']:
                print("Warning! Multiple parent node leads to this!")
                print("Answer %d from question %d was referenced by" % (nextAnswerID, nextID))
                print("question %d answer %d." % frps[nextID][nextAnswerID])
                exit()
            frps[nextID][nextAnswerID]['prev'] = (questionID, answerID)

##############################################################################
# examine each route from FRPS, generate questions and classifications

for questionID in frps:
    for answerID in range(0, len(frps[questionID])):
        q = frps[questionID][answerID]

        if answerID == 0:
            print ("%3d(%1d)" % (questionID, answerID + 1))
            t = True
        else:
            print ("   (%1d)" % (answerID + 1))

        if q['prev'] != None:
            print ('(from %d:%d)' % (q['prev'][0], q['prev'][1] + 1))

        print (q['desc'],)
        print ('--> [%s]' % (-1 != q['next'] and q['next'] or q['result']))

        if q['next'] < 0:
            cls = newClassification(outputpath, q['result'])
            cls.save()
