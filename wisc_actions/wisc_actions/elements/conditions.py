from .base import WiscBase

class Condition(object):
    '''
    Encoding for conditions.
    '''

    keys = [set(('thing','property'))]

    def __init__(self,thing,property):
        self.thing = thing
        self.property = property

    def evaluate(self,state):
        '''
        Search in the state for the thing,
        '''
        return False

    def execute(self,state):
        '''
        Modify the state
        '''
        return state
