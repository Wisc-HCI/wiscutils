from enum import Enum
from .base import WiscBase
from .parse import parse
from .things import Property

class Operation(Enum):

    @classmethod
    def load(cls,serialized):
        for op in cls:
            if op.value == serialized:
                return op

    @property
    def serialized(self):
        return self.value

class PropertyOperation(Operation):
    EQUALS = '=='
    NOT_EQUALS = '!='
    GREATER_THAN = '>'
    GREATER_THAN_OR_EQUALS = '>='
    LESS_THAN = '<'
    LESS_THAN_OR_EQUALS = '<='
    EXISTS = 'exists'

class LTLOperation(Operation):
    NOT = '!'            # [Unary]: Inverts condition.
    NEXT = 'X'           # LTL [Unary]: Condition has to hold at the next state.
    FINALLY = 'F'        # LTL [Unary]: Condition eventually has to hold (somewhere on the subsequent path).
    GLOBALLY = 'G'       # LTL [Unary]: Condition has to hold on the entire subsequent path.
    UNTIL = 'U'          # LTL [Binary]: Condition A has to hold at least until the other condition B becomes true, which must hold at the current or a future position.
    RELEASE = 'R'        # LTL [Binary]: Condition A has to be true until and including the point where another condition B first becomes true; if B never becomes true, A must remain true forever.
    WEAK_UNTIL = 'W'     # LTL [Binary]: Condition A has to hold at least until B; if B never becomes true, A must remain true forever.
    STRONG_RELEASE = 'M' # LTL [Binary]: Condition A has to be true until and including the point where B first becomes true, which must hold at the current or a future position.


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

    @classmethod
    def load(cls,serialized):
        return Condition(property=Property.load(serialized['property']),
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
