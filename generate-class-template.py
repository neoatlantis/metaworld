#!/usr/bin/env python3

import os
import sys

from metaworld.mwquestion import Question
from metaworld.mwclass import Classification

try:
    dbpath = os.path.realpath(sys.argv[1])
    name = sys.argv[2]
except:
    print("python generate-class-template.py <DATABASE PATH> <CLASS NAME>")

chars = {}

questions = {}
questionsPath = os.path.join(dbpath, 'question')
questionsDir = os.listdir(questionsPath)
for fn in questionsDir:
    qid = int(fn.split('-')[0])
    questions[qid] = Question(dbpath)
    questions[qid].open(qid)

# generate a template

for qid in questions:
    question = questions[qid]
    qrepr = question.getQuestionPresentation()
    qname = qrepr['name']
    
    chars[qid] = []
    
    print(qname)



# derive output
output = {
    'name': name,
    'chars': chars,
}


