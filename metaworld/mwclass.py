#!/usr/bin/env python3

import re
import os
import sys
import yaml

from .mwquestion import Question

def readAttributes(atom):
    ret = {
        'freq': 1.0
    }
    if 'freq' in atom:
        ret['freq'] = {
            'often': 1.0,
            'sometimes': 0.5,
            'rare': 0.25,
        }[atom['freq']]
    return ret

def getAllCharDefinitions(defobj):
    """Given an input as entry in a characteristic definition, interprete
    and yield all standard answers. A single standard answer can be denoted:
        1. using a simple string or integer, as direct answer. For `choose`
           and `range` questions this always works.
        2. using a dict:
          2.1 containing `def` key. Their value will be
              interpreted as standard answers.
          2.2 containing other attributes, which controls the calculation
              process only.
    The input is one direct standard answer denotation, or a list of them.
    """
    objtype = type(defobj)
    def readAtom(atom):
        if type(atom) == dict:
            return (atom["def"], readAttributes(atom))
        elif type(atom) in [str, int]:
            return (atom, readAttributes({}))
        else:
            raise Exception("Invalid character definition.")

    if objtype == list:
        for each in defobj: yield readAtom(each)
    else:
        yield readAtom(defobj)
        

class Classification:
    """Represents a classification in our system."""

    def __init__(self, dbpath, **argv):
        self.__basedbpath = os.path.realpath(dbpath)
        self.__dbpath = os.path.join(self.__basedbpath, 'class')

        if not os.path.isdir(self.__dbpath):
            raise Exception("Database not initialized properly.")

        self.name = ''
        self.chars = {}

        if argv:
            # we are being initialized with parameters.
            self.name = argv['name']
            self.id = self.__allocateID()
            self.__filename = os.path.join(self.__dbpath, "%04d-%s.yaml" % (
                self.id,
                self.__findFilenameDescription(self.name)
            ))

    def open(self, classid):
        """Open the classification file stored in `self.__dbpath`, which is
        determined by the id."""
        # find the file
        classid = "%03d" % classid
        dirlist = os.listdir(self.__dbpath)
        found = None
        for fn in dirlist:
            if fn.endswith('.yaml') and fn.startswith(classid):
                found = fn
                break
        if not found:
            raise Exception("Classification #%s not found." % classid)

        # read yaml into our class
        self.__filename = os.path.join(self.__dbpath, found)
        doc = yaml.load(open(self.__filename).read())

        # get necessary info
        self.id = int(classid)
        self.name = doc['name']

        # examine chars(answers) definition
        chars = doc['chars']

        self.chars = {}
        self.questions = {}
        for qid in chars: # for each question mentioned
            intqid = int(qid)
            # retrieve the question
            try:
                question = Question(self.__basedbpath)
                question.open(qid)
                self.questions[intqid] = question
                self.chars[intqid] = []
            except Exception as e:
                raise Exception("Characteristics definition error: %s" % e)
            # iterate over characteristics(can be multiple) under one question
            chardefIterator = getAllCharDefinitions(chars[qid])
            for standardAnswer, answerAttributes in chardefIterator:
                if not question.verifyStandardAnswer(standardAnswer):
                    raise Exception("Standard answer definition error.")
                self.chars[intqid].append((
                    standardAnswer,
                    answerAttributes
                ))

    def __allocateID(self):
        """Allocates a 4-digits numeric ID for this classification, basing on
        existing classifications in `self.__dbpath`."""
        dirlist = os.listdir(self.__dbpath)
        maxid = 0
        for each in dirlist:
            if not each.endswith('.yaml'): continue
            try:
                gotid = int(each.split('-')[0])
                if gotid > maxid: maxid = gotid
            except:
                continue
        return maxid + 1

    def __findFilenameDescription(self, name):
        """Provide a suggestion on filename based on `name`."""
        # TODO filter the name, may be convert to latin names?
        return name[:30]

    def save(self):
        """Save the classification using a human-friendly name."""
        # TODO chars has to be updated to new format accordingly.
        obj = {
            'name': self.name,
            'chars': self.chars,
        }
        doc = yaml.dump(obj, default_flow_style=False, allow_unicode=True)
        open(self.__filename, 'w+').write(doc)
        return self.__filename
    
def newClassification(dbpath, name):
    return Classification(dbpath, name=name)
