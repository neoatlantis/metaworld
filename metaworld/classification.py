#!/usr/bin/env python3

import re
import os
import sys
import yaml



class Classification:
    """Represents a classification in our system."""

    def __init__(self, dbpath, **argv):
        self.__dbpath = os.path.join(os.path.realpath(dbpath), 'class')
        if not os.path.isdir(self.__dbpath):
            raise Exception("Database not initialized properly.")

        if argv:
            # we are being initialized with parameters.
            self.name = argv['name']
            self.id = self.__allocateID()
            self.chars = []
            self.__filename = os.path.join(self.__dbpath, "%04d-%s.yaml" % (
                self.id,
                self.__findFilenameDescription(self.name)
            ))

    def open(self, classid):
        """Open the classification file stored in `self.__dbpath`, which is
        determined by the id."""
        # find the file
        classid = "%04d" % classid
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
        doc = yaml.load(self.__filename)

        # get necessary info
        self.id = int(doc['id'])
        if int(classid) != self.id:
            raise Exception(
                "Classification file %s has inconsistent id " % found + \
                "between filename and content.")            
        self.name = doc['name']
        self.chars = doc['chars']
        # TODO examine chars(answers) definition

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
        obj = {
            'name': self.name,
            'id': self.id,
            'chars': self.chars,
        }
        doc = yaml.dump(obj, default_flow_style=False, allow_unicode=True)
        open(self.__filename, 'w+').write(doc)
        return self.__filename
    
def newClassification(dbpath, name):
    return Classification(dbpath, name=name)
