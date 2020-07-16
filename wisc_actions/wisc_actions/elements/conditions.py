from .base import WiscBase
from enum import Enum
from .properties import Property

class Operation(Enum):
    EQUALS = '=='
    NOT_EQUALS = '!='
    GREATER_THAN = '>'
    GREATER_THAN_OR_EQUALS = '>='
    LESS_THAN = '<'
    LESS_THAN_OR_EQUALS = '<='
    EXISTS = 'exists'

    @classmethod
    def load(cls,serialized):
        for op in Operation:
            if op.value == serialized:
                return op

    @property
    def serialized(self):
        return self.value

class Condition(WiscBase):
    '''
    Encoding for conditions.
    '''

    keys = [set(('thing','property','operation'))]

    def __init__(self,thing,property,operation):
        self.thing = thing
        self.property = property
        self.operation = Operation

    @classmethod
    def load(cls,serialized):
        return Condition(thing=serialized['thing'],
                         property=Property.load(serialized['property']),
                         operation=Operation.load(serialized['operation']))

    def evaluate(self,state):
        '''
        Check to see if hte condition is satisfied.
        '''
        return False

    def execute(self,state):
        '''
        Modify the state
        '''
        return state
