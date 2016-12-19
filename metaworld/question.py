#!/usr/bin/env python3

import yaml
import sys
import os



class IllegalTreeDefinition(Exception): pass
class QuestionDefinitionError(Exception): pass
class InvalidStandardAnswer(Exception): pass

##############################################################################
# Type of Question: `choose`

def getAllNodes(parents, i0, tree):
    """Return all leaves from a tree, with their corresponding ids and parents.
    A tree node can be:
        1. a single string, this equals a list with one single string.
        2. a list containing strings or lists of strings(synonyms).
        3. a dict, whose keys are string nodes and dict[key] are sub-nodes.
    Leaves are identified by their IDs. Two leaves may have identical ID, which
    means they are synonyms. Otherwise they must be different.

    Returns ([parents], nodeID, nodeString)
    """
    isLeaf = lambda i: type(i) in [str, unicode]

    if isLeaf(tree):
        yield (parents, i0+1, tree)
    elif type(tree) == list:
        if len(tree) < 1:
            raise IllegalTreeDefinition("empty list")
        i = i0 
        for node in tree:
            if isLeaf(node):
                i += 1
                yield (parents, i, node)
            elif type(node) == list: # list inside list => synonyms
                i += 1
                for parallelNode in node: # enumerate all synonyms
                    if not isLeaf(parallelNode):
                        raise IllegalTreeDefinition(
                            "parallel node must be leaves."
                        )
                    yield (parents, i, parallelNode) # NOTICE `i` is same
            else:
                raise IllegalTreeDefinition("invalid node")
    elif type(tree) == dict:
        i = i0
        for node in tree:
            i += 1
            yield (parents, i, node)
            iterator = getAllNodes(parents + [i], i, tree[node])
            for subnodeResult in iterator:
                i += 1
                yield subnodeResult # yield results from sub iterator
    else:
        raise IllegalTreeDefinition("invalid node")

"""test = {
    '1': ['1.1', '1.2'],
    '2': {
        '2.1': ['2.1.1'],
        '2.2': '2.2.1',
    }
}
for p, i, c in getAllNodes([], 0, test):
    print (p, i, c)"""

class ChooseTypeQuestion:
    """A choose type question represents such a way of input, that all
    possible answers are structured in a plain or nested way.
    """

    def __init__(self, definition):
        """Initialize the instance using `definition`."""
        try:
            choices = {}
            for parents, i, choice in getAllNodes([], 0, definition):
                if choice in choices:
                    raise Exception(
                        "Ambiguitical choice defined - " + \
                        "no any 2 choices may have same text."
                    )
                choices[choice] = (parents, i)
        except Exception,e:
            raise QuestionDefinitionError(e)
        self.__choices = choices
        self.__tree = definition

    def dumpDefinition(self):
        return self.__tree
    
    def getQuestionPresentation(self):
        """Presents the question in a way suitable for generating UI."""
        return {
            'type': 'choose',
            'tree': self.__tree,
            'plain': self.__choices.keys(),
        }

    def verifyStandardAnswer(self, standardAnswer):
        """Verify if a standard answer definition is legal according to the
        question. A standard answer is the one defined in any classification
        profile. This method provides the way examing if such a definition
        is acceptable: if the choice exists."""
        return standardAnswer in self.__choices

    def calculatePoints(self, standardAnswer, userAnswer):
        """Calculate the actual points basing on standard answer and user
        input. Returns a float point ranging from between 0 and 1."""
        if not self.verifyStandardAnswer(standardAnswer):
            raise InvalidStandardAnswer()
        if not userAnswer in self.__choices: return 0
        saParents, saID = self.__choices[standardAnswer]
        uaParents, uaID = self.__choices[userAnswer]
        if saID == uaID or saID in uaParents:
            # if user answer is no less specific as standard answer
            return 1.0
        elif uaID in saParents:
            # if user answer covers standard answer, but not specific enough
            x = saParents.index(uaID) + 1  # x = 1,2,3...s-1, s >= 2
            s = len(saParents) + 1         # so 1/s <= x/s <= s-1/s
            return 1.0 * x / s
        return 0.0


##############################################################################
# Type of Question: `range`

class RangeTypeQuestion:
    """A range type question represents such a way of input, that the
    input must be an integer within a given range.
    """

    def __verifyAndGetRange(self, definition):
        try:
            maximum, minimum = False, False
            if 'min' in definition:
                minimum = definition['min']
                assert type(minimum) == int
            if 'max' in definition:
                maximum = definition['max']
                assert type(maximum) == int
            if not (maximum is False or minimum is False):
                assert minimum <= maximum
        except:
            return None
        return (minimum, maximum)

    def __init__(self, definition):
        """Initialize the instance using `definition`."""
        ret = self.__verifyAndGetRange(definition)
        if not ret: 
            raise QuestionDefinitionError('Invalid range definition.')
        self.__min, self.__max = ret 
    
    def getQuestionPresentation(self):
        """Presents the question in a way suitable for generating UI."""
        return {
            'type': 'range',
            'max': self.__max,
            'min': self.__min,
        }

    def dumpDefinition(self):
        ret = {'min': False, 'max': False}
        if self.__max: ret['max'] = self.__max
        if self.__min: ret['min'] = self.__min
        return ret

    def verifyStandardAnswer(self, standardAnswer):
        """Verify if a standard answer definition is legal according to the
        question. A standard answer is the one defined in any classification
        profile. This method provides the way examing if such a definition is
        acceptable: if the given range is within our question definition."""
        # get range in standard answer
        rng = self.__verifyAndGetRange(standardAnswer)
        if not rng: return False
        saMin, saMax = rng
        # verify this range within question range
        if not self.__max is False and saMax > self.__max: return False
        if not self.__min is False and saMin < self.__min: return False
        return True

    def calculatePoints(self, standardAnswer, userAnswer):
        """Calculate the actual points basing on standard answer and user
        input. Returns a float point ranging from between 0 and 1."""
        if not self.verifyStandardAnswer(standardAnswer):
            raise InvalidStandardAnswer()
        saMin, saMax = self.__verifyAndGetRange(standardAnswer)
        if type(userAnswer) != int: return 0.0
        if not saMax is False and userAnswer > saMax: return 0.0
        if not saMin is False and userAnswer < saMin: return 0.0
        return 1.0


##############################################################################
# Generic handler of questions

class Question:
    
    def __init__(self, dbpath, **argv):
        self.__dbpath = os.path.join(os.path.realpath(dbpath), 'question')
        if not os.path.isdir(self.__dbpath):
            raise Exception("Database not initialized properly.")

        self.category = ''
        self.name = ''

        if argv:
            # we are being initialized with parameters.
            self.name = argv['name']
            if 'category' in argv: self.category = argv['category']
            self.id = self.__allocateID()
            self.__filename = os.path.join(self.__dbpath, "%04d-%s.yaml" % (
                self.id,
                self.__findFilenameDescription(self.name)
            ))

    def open(self, qid):
        """Open the classification file stored in `self.__dbpath`, which is
        determined by the id."""
        # find the file
        qid = "%03d" % qid
        dirlist = os.listdir(self.__dbpath)
        found = None
        for fn in dirlist:
            if fn.endswith('.yaml') and fn.startswith(qid):
                found = fn
                break
        if not found:
            raise Exception("Question #%s not found." % qid)

        # read yaml into our class
        self.__filename = os.path.join(self.__dbpath, found)
        doc = yaml.load(open(self.__filename).read())

        # get necessary info
        self.name = doc['name']
        if 'category' in doc: self.category = doc['category']
        
        if 'choose' in doc:
            self.__core = ChooseTypeQuestion(doc['choose'])
        elif 'range' in doc:
            self.__core = RangeTypeQuestion(doc['range'])
        else:
            raise QuestionDefinitionError('no specific question defined.')

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
        obj = { 'name': self.name, 'category': self.category }
        if self.__core is ChooseTypeQuestion:
            obj['choose'] = self.__core.dumpDefinition()
        elif self.__core is RangeTypeQuestion:
            obj['range'] = self.__core.dumpDefinition()

        doc = yaml.dump(obj, default_flow_style=False, allow_unicode=True)
        open(self.__filename, 'w+').write(doc)
        return self.__filename

    def getQuestionPresentation(self):
        return self.__core.getQuestionPresentation()

    def verifyStandardAnswer(self, standardAnswer):
        return self.__core.verifyStandardAnswer(standardAnswer)

    def calculatePoints(self, standardAnswer, userAnswer):
        return self.__core.calculatePoints(standardAnswer, userAnswer)



if __name__ == '__main__':
    from tabulate import tabulate

    try:
        dbpath = sys.argv[1]
        qid = int(sys.argv[2])
    except:
        print "Open a question: python question.py <DatabasePath> <QuestionID>"
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
        print tabulate(answers, headers=['Standard\\UserAns'] + qrepr['plain'])


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
