#!/usr/bin/env python3

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
