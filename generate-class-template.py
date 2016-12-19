#!/usr/bin/env python3

import os
import sys
import yaml
import uuid

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

##############################################################################
# generate a template

# ---- prepare comments to be inserted into final document
hintReplacement = {}
hint = {}
def documentQuestion(qrepr):
    """Generate a document on this question."""
    qname = qrepr['name']
    qtype = qrepr['type']
    return qname

def indentDocumentComment(src, indent):
    return ['\n', ' ' * indent + '#' + src]

# ---- prepare document

for qid in questions:
    question = questions[qid]
    qrepr = question.getQuestionPresentation()
    qname = qrepr['name']
    qtype = qrepr['type']
    
    fakeqid = '*fakestart*' + str(uuid.uuid1()) + '*fakeend*'
    hintReplacement[fakeqid] = qid
    hint[fakeqid] = documentQuestion(qrepr)

    chars[fakeqid] = []
    
    if 'choose' == qtype:
        choices = qrepr['plain']
        if len(choices) <= 2:
            for each in choices:
                chars[fakeqid].append(each)
        else:
            chars[fakeqid].append(choices[0])
            chars[fakeqid].append(choices[1])
            chars[fakeqid].append({ 'def': choices[2], 'freq': 'sometimes' })
            
    elif 'range' == qtype:
        pass

# ---- derive output

output = {
    'chars': chars,
}

outputstr = yaml.dump(output, default_flow_style=False, allow_unicode=True)

# ---- replace comments

lines = outputstr.split('\n')
newlines = []

for line in lines:
    indent = line.find('*fakestart*')
    if indent < 0:
        newlines.append(line)
        continue
    fakeend = line.find('*fakeend*')
    fakeqid = line[indent: fakeend-indent+12]
    qid = hintReplacement[fakeqid]

    newlines += indentDocumentComment(hint[fakeqid], indent-1)
    newlines.append(line.replace("'%s'" % fakeqid, "%d" % qid))

outputstr = "name: %s\n" % name + '\n'.join(newlines)
print(outputstr)
