from enum import Enum
from .structures import *

class Operator(Enum):

    EQUALS = '=='
    NOT_EQUALS = '!='
    GREATER_THAN = '>'
    GREATER_THAN_OR_EQUALS = '>='
    LESS_THAN = '<'
    LESS_THAN_OR_EQUALS = '<='
    EXISTS = 'exists'
    NOT = '!'            # [Unary]: Inverts condition.
    NEXT = 'X'           # LTL [Unary]: Condition has to hold at the next state.
    FINALLY = 'F'        # LTL [Unary]: Condition eventually has to hold (somewhere on the subsequent path).
    GLOBALLY = 'G'       # LTL [Unary]: Condition has to hold on the entire subsequent path.
    UNTIL = 'U'          # LTL [Binary]: Condition A has to hold at least until the other condition B becomes true, which must hold at the current or a future position.
    RELEASE = 'R'        # LTL [Binary]: Condition A has to be true until and including the point where another condition B first becomes true; if B never becomes true, A must remain true forever.
    WEAK_UNTIL = 'W'     # LTL [Binary]: Condition A has to hold at least until B; if B never becomes true, A must remain true forever.
    STRONG_RELEASE = 'M' # LTL [Binary]: Condition A has to be true until and including the point where B first becomes true, which must hold at the current or a future position.
    ADD = '+'            # MATH
    SUBTRACT = '-'       # MATH
    MULTIPLY = 'x'       # MATH
    DIVIDE = '/'         # MATH
    POWER = '^'          # MATH
    MODULUS = '%'        # MATH
    CARTESIAN_DISTANCE = 'cartesian_dist'    # MATH
    ANGULAR_DISTANCE = 'angular_dist'        # MATH
    OBSERVE = 'observe'
    ACCESS = 'access'
    UNION = 'U'          # SETS
    INTERSECTION = 'I'   # SETS

    @classmethod
    def load(cls,serialized):
        for op in cls:
            if op.value == serialized:
                return op

    @property
    def serialized(self):
        return self.value

def access(container,accessor):
    # If accessor is a Term, get the string name
    try:
        accessor = accessor.name
    except:
        pass

    # Check for various methods of accessing
    try:
        # Check properties of the Thing
        for property in container.properties:
            if property.name == accessor:
                return property
    except:
        if isinstance(container,dict):
            # Check keys of the dictionary
            for key,value in container.items():
                if key == accessor:
                    return value
        elif isinstance(container,(list,Enumerable)) and isinstance(accessor,int):
            # Return the value at the index of the enumerable
            return container[accessor]
        elif isinstance(container,(Position,Orientation,Pose)):
            getattr(container, accessor, None)
    # If not found, return None
    return None

def observe(description,context):
    observable = []
    for item in context.state:
        found = False
        for property in item.properties:
            if EXECUTION[description.operator](property,description.property,context):
                found = True
        if found:
            observable.append(item)
    return observable


EXECUTION = {
    Operator.ADD:lambda term_a, term_b, context: Operation.resolve(term_a,context) + Operation.resolve(term_b,context),
    Operator.SUBTRACT:lambda term_a, term_b, context: Operation.resolve(term_a,context) - Operation.resolve(term_b,context),
    Operator.MULTIPLY:lambda term_a, term_b, context: Operation.resolve(term_a,context) * Operation.resolve(term_b,context),
    Operator.DIVIDE:lambda term_a, term_b, context: Operation.resolve(term_a,context) / Operation.resolve(term_b,context),
    Operator.POWER:lambda term_a, term_b, context: Operation.resolve(term_a,context) ** Operation.resolve(term_b,context),
    Operator.MODULUS:lambda term_a, term_b, context: Operation.resolve(term_a,context) % Operation.resolve(term_b,context),
    Operator.CARTESIAN_DISTANCE:lambda term_a, term_b, context: Operation.resolve(term_a,context).distance_to(Operation.resolve(term_b,context)),
    Operator.ANGULAR_DISTANCE:lambda term_a, term_b, context: Operation.resolve(term_a,context).distance_to(Operation.resolve(term_b,context)),
    Operator.EQUALS:lambda term_a, term_b, context: Operation.resolve(term_a,context) == Operation.resolve(term_b,context),
    Operator.NOT_EQUALS:lambda term_a, term_b, context: Operation.resolve(term_a,context) != Operation.resolve(term_b,context),
    Operator.GREATER_THAN:lambda term_a, term_b, context: Operation.resolve(term_a,context) > Operation.resolve(term_b,context),
    Operator.GREATER_THAN_OR_EQUALS:lambda term_a, term_b, context: Operation.resolve(term_a,context) >= Operation.resolve(term_b,context),
    Operator.LESS_THAN:lambda term_a, term_b, context: Operation.resolve(term_a,context) < Operation.resolve(term_b,context),
    Operator.LESS_THAN_OR_EQUALS:lambda term_a, term_b, context: Operation.resolve(term_a,context) <= Operation.resolve(term_b,context),
    Operator.EXISTS:lambda term_a, term_b, context: context.exists(term_a),
    Operator.ACCESS:lambda term_a, term_b, context: access(Operation.resolve(term_a,context),Operation.resolve(term_b,context)),
    Operator.OBSERVE:lambda term_a, term_b, context: observe(term_a,context),
    Operator.UNION:lambda term_a, term_b, context: [term for term in Operation.resolve(term_a,context) if term not in Operation.resolve(term_b,context)]+[term for term in Operation.resolve(term_b,context)],
    Operator.INTERSECTION:lambda term_a, term_b, context: [term for term in Operation.resolve(term_a,context) if term in Operation.resolve(term_b,context)],
}

class Operation(WiscBase):
    '''
    Class for defining operators
    '''

    keys = [{'term_a','term_b','operator'}]

    def __init__(self,term_a,term_b=None,operator=None):
        self.binary = False
        self.term_a = term_a
        self.term_b = term_b
        if self.term_b != None:
            self.binary = True
        else:
            assert operator in [Operator.EXISTS,Operator.OBSERVE]
        self.operator = operator

    @classmethod
    def load(cls, serialized: dict, context: list):
        '''
        TODO: handle whatever context-grabbing implementation we use here for
        non-math terms.
        '''
        return Operation(term_a=parse([Operation],serialized['term_a']),
                         term_b=parse([Operation],serialized['term_b']),
                         operator=Operator.load(serialized['operator']))

    @property
    def serialized(self):
        return {'term_a':self.term_a.serialized,
                'term_b':self.term_b.serialized if self.binary else None,
                'operator':self.operator.serialized
                }

    def execute(self,context):
        return EXECUTION[self.operator](self.term_a, self.term_b, context)

    @classmethod
    def resolve(self,term,context):
        if isinstance(term,(int,float,list)):
            return term
        if term.keys == [{'name'}]:
            # term is a Term
            return context.get(term)
        elif isinstance(term,Operation):
            return term.execute(context)
        elif isinstance(term,WiscBase):
            return term

    def __add__(self,other):
        if isinstance(other,(WiscBase,int,float)):
            return Operation(self,other,Operator.ADD)
        else:
            return None

    def __sub__(self,other):
        if isinstance(other,(WiscBase,int,float)):
            return Operation(self,other,Operator.SUBTRACT)
        else:
            return None

    def __mul__(self,other):
        if isinstance(other,(WiscBase,int,float)):
            return Operation(self,other,Operator.MULTIPLY)
        else:
            return None

    def __truediv__(self,other):
        if isinstance(other,(WiscBase,int,float)):
            return Operation(self,other,Operator.DIVIDE)
        else:
            return None

    def __mod__(self,other):
        if isinstance(other,(WiscBase,int,float)):
            return Operation(self,other,Operator.MODULUS)
        else:
            return None

    def __lt__(self,other):
        if isinstance(other,(WiscBase,int,float)):
            return Operation(self,other,Operator.LESS_THAN)
        else:
            return None

    def __le__(self,other):
        if isinstance(other,(WiscBase,int,float)):
            return Operation(self,other,Operator.LESS_THAN_OR_EQUALS)
        else:
            return None

    def __gt__(self,other):
        if isinstance(other,(WiscBase,int,float)):
            return Operation(self,other,Operator.GREATER_THAN)
        else:
            return None

    def __ge__(self,other):
        if isinstance(other,(WiscBase,int,float)):
            return Operation(self,other,Operator.GREATER_THAN_OR_EQUALS)
        else:
            return None

    def __eq__(self,other):
        if isinstance(other,(WiscBase,int,float)):
            return Operation(self,other,Operator.EQUALS)
        else:
            return None
