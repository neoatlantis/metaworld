#!/usr/bin/env python3

class QuestionDefinitionError(Exception): pass
class InvalidStandardAnswer(Exception): pass

##############################################################################
# Type of Question: `choose`

def getAllNodes(parents, i0, tree):
    """Return all nodes and subnodes from a tree, with their corresponding
    ids and parents. A tree can be:
        1. a single string, this equals a list with one single string.
        2. a list contains and only contains strings.
        3. a dict, whose keys are nodes and dict[key] are sub-trees.
    Returns ([parents], nodeID, nodeString)
    """
    if type(tree) == str:
        yield (parents, i0+1, tree)
    elif type(tree) == list:
        if len(tree) < 1:
            raise Exception("Illegal tree definition.")
        i = i0 
        for node in tree:
            if type(node) == str:
                i += 1
                yield (parents, i, node)
            else:
                raise Exception("Illegal tree definition.")
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
        raise Exception("Illegal tree definition.")

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
    
    def getQuestionPresentation(self):
        """Presents the question in a way suitable for generating UI."""
        return {
            'type': 'choose',
            'choices': self.__tree
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
# Type of Question: Range

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
    
    def __init__(self, **argv):
        self.__redirected = None
        pass

    def fromJSON(self, strJSON):
        pass

    def fromYAML(self, strYAML):
        pass

    def setRedirection(self, newQuestionInstance):
        """Tell this question has been redirected to another one. Happens
        when this instance was merged with another."""
        self.__redirected = newQuestionInstance

    def getAnswerReference(self, answer):
        """Get a reference to an answer in this question. This references
        normally the questionID of this instance and the corresponding
        answerID, but if our instance was merged with another question
        instance, this query will be redirected to the new merged instance."""
        if self.__redirected:
            return self.__redirected.getAnswerReference(answer)
        # TODO get answer reference


    def __add__(self, other):
        """Define the add method to merge one question with another. The merged
        question will have a new questionID, but old question instances can
        still be answered, which will generate a new link to this new merged
        instance."""

        newInstance = Question() # TODO argv
        
        self.setRedirection(newInstance)
        other.setRedirection(newInstance)
        return newInstance
