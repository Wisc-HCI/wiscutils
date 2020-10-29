from .base import WiscBase
from .things import Property
from .operations import Operator, Operation

class Condition(WiscBase):
    '''
    Encoding for logic
    '''

    keys = [{'operator'}]

    def __init__(self,operator:Operator):
        self.operator = operator

class Description(Condition):
    '''
    Encoding for thing-agnostic property attributes.
    '''
    keys = [{'property','operator'}]

    def __init__(self,property:Property,operator:Operator):
        super(Description,self).__init__(operator)
        self.property = property
        self.operator = operator

    @classmethod
    def load(cls, serialized: dict, context: list):
        return Description(property=Property.load(serialized['property'],context),
                           operator=Operator.load(serialized['operator'],context))

    @property
    def serialized(self):
        return {'property':self.property.serialized,
                'operator':self.operator.serialized
                }

    def observe(self):
        return Operation(self,None,Operator.OBSERVE)

    def union(self,other):
        return Operation(self.observe(),other.observe(),Operator.UNION)

    def intersection(self,other):
        return Operation(self.observe(),other.observe(),Operator.INTERSECTION)

class PropertyCondition(Condition):
    '''
    Encoding for thing-property comparison conditions.
    '''

    keys = [{'thing','property','operator'}]

    def __init__(self,thing:str,property:Property,operator:Operator):
        super(PropertyCondition,self).__init__(operator)
        self.thing = thing
        self.property = property

    @classmethod
    def load(cls, serialized: dict, context: list):
        return PropertyCondition(thing=serialized['thing'],
                                 property=parse([Property],serialized['property'],context),
                                 operator=parse([Operator],serialized['operator'],context))

    @property
    def serialized(self):
        return {'thing':self.thing,
                'property':self.property.serialized,
                'operator':self.operator.serialized
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
    Encoding for unary LTL conditions. Consists of a condition and a unary LTL operator.
    '''
    keys = [{'condition','operator'}]

    def __init__(self,condition,operator):
        self.condition = condition
        self.operator = operator

    @classmethod
    def load(cls,serialized):
        return UnaryCondition(condition=WiscBase.parse([Condition,UnaryLTLCondition,BinaryLTLCondition],serialized['condition']),
                              operator=Operator.load(serialized['operator']))

    @property
    def serialized(self):
        return {'condition':self.condition.serialized,
                'operator':self.operator.serialized
                }

class BinaryLTLCondition(Condition):
    '''
    Encoding for binary LTL conditions. Consists of two conditions (a/b) and a binary LTL operator.
    '''

    keys = [{'condition_a','condition_b','operator'}]

    def __init__(self,condition_a,condition_b,operator):
        self.condition_a = condition_a
        self.condition_b = condition_b
        self.operator = operator

    @classmethod
    def load(cls,serialized):
        return BinaryCondition(condition_a=WiscBase.parse([PropertyCondition,UnaryLTLCondition,BinaryLTLCondition],serialized['condition_a']),
                               condition_b=WiscBase.parse([PropertyCondition,UnaryLTLCondition,BinaryLTLCondition],serialized['condition_b']),
                               operator=Operator.load(serialized['operator']))

    @property
    def serialized(self):
        return {'condition_a':self.condition_a.serialized,
                'condition_b':self.condition_b.serialized,
                'operator':self.operator.serialized
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
