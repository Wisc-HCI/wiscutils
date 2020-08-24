from .base import WiscBase
from .parse import parse
from .things import Property
from .operations import Operation, PropertyOperation, LTLOperation

class Condition(WiscBase):
    '''
    Encoding for logic
    '''

    keys = [set(('operation'))]

    def __init__(self,operation:Operation):
        self.operation = operation

class Description(Condition):
    '''
    Encoding for thing-agnostic property attributes.
    '''
    keys = [set(('property','operation'))]

    def __init__(self,property:Property,operation:PropertyOperation):
        super(Description,self).__init__(operation)
        self.property = property
        self.operation = operation

    @classmethod
    def load(cls,serialized):
        return Description(property=Property.load(serialized['property']),
                           operation=Operation.load(serialized['operation']))

    @property
    def serialized(self):
        return {'property':self.property.serialized,
                'operation':self.operation.serialized
                }

class PropertyCondition(Condition):
    '''
    Encoding for thing-property comparison conditions.
    '''

    keys = [set(('thing','property','operation'))]

    def __init__(self,thing:str,property:Property,operation:Operation):
        super(PropertyCondition,self).__init__(operation)
        self.thing = thing
        self.property = property

    @classmethod
    def load(cls,serialized):
        return PropertyCondition(thing=serialized['thing'],
                                 property=parse([Property],serialized['property']),
                                 operation=parse([Operation,LTLOperation],serialized['operation']))

    @property
    def serialized(self):
        return {'thing':self.thing,
                'property':self.property.serialized,
                'operation':self.operation.serialized
        }

    def evaluate(self,state):
        '''
        Check to see if the condition is satisfied.
        '''
        return False

    def execute(self,state):
        '''
        Modify the state
        '''
        return state

class UnaryLTLCondition(Condition):
    '''
    Encoding for unary LTL conditions. Consists of a condition and a unary LTL operation.
    '''
    keys = [set(('condition','operation'))]

    def __init__(self,condition,operation):
        self.condition = condition
        self.operation = operation

    @classmethod
    def load(cls,serialized):
        return UnaryCondition(condition=parse([Condition,UnaryLTLCondition,BinaryLTLCondition],serialized['condition']),
                              operation=LTLOperation.load(serialized['operation']))

    @property
    def serialized(self):
        return {'condition':self.condition.serialized,
                'operation':self.operation.serialized
                }

class BinaryLTLCondition(Condition):
    '''
    Encoding for binary LTL conditions. Consists of two conditions (a/b) and a binary LTL operation.
    '''

    keys = [set(('condition_a','condition_b','operation'))]

    def __init__(self,condition_a,condition_b,operation):
        self.condition_a = condition_a
        self.condition_b = condition_b
        self.operation = operation

    @classmethod
    def load(cls,serialized):
        return BinaryCondition(condition_a=parse([PropertyCondition,UnaryLTLCondition,BinaryLTLCondition],serialized['condition_a']),
                               condition_b=parse([PropertyCondition,UnaryLTLCondition,BinaryLTLCondition],serialized['condition_b']),
                               operation=LTLOperation.load(serialized['operation']))

    @property
    def serialized(self):
        return {'condition_a':self.condition_a.serialized,
                'condition_b':self.condition_b.serialized,
                'operation':self.operation.serialized
                }

    def evaluate(self,state):
        '''
        Check to see if the condition is satisfied.
        '''
        return False

    def execute(self,state):
        '''
        Modify the state
        '''
        return state
