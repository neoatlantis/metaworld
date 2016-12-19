#!/usr/bin/env python3

import sys
import os

from tabulate import tabulate

from metaworld.mwquestion import Question


try:
    dbpath = sys.argv[1]
    qid = int(sys.argv[2])
except:
    print("Open a question: python mwquestion.py <DatabasePath> <QuestionID>")
    exit(1)

question = Question(dbpath)
question.open(qid)

qrepr = question.getQuestionPresentation()

print("Question: %s" % question.name)
print("Category: %s" % question.category)

if 'choose' == qrepr['type']:
    print("Choose one from followings:")
    answers = []
    for i in qrepr['plain']:
        print(" - %s" % i)
        row = [i]
        for j in qrepr['plain']:
            row.append(
                question.calculatePoints(i, j)
            )
        answers.append(row)
    print("\nCalculate points using Standard Answer - User Answer:")
    print(tabulate(answers, headers=['Standard\\UserAns'] + qrepr['plain']))


if 'range' == qrepr['type']:
    print("Input an integer.")

    if qrepr['min'] is False:
        print (" - No lower limit on input.")
    else:
        print (" - Must be no smaller than %d." % qrepr['min'])

    if qrepr['max'] is False:
        print (" - No upper limit on input.")
    else:
        print (" - Must no larger than %d." % qrepr['max'])

print ("\nCompiled JS:\n%s" % question.compileToJS())
