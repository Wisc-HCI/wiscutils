from .operations import MathOperation
from .base import WiscBase

EXECUTION = {
    MathOperation.ADD:lambda term_a, term_b: term_a + term_b,
    MathOperation.SUBTRACT:lambda term_a, term_b: term_a - term_b,
    MathOperation.MULTIPLY:lambda term_a, term_b: term_a * term_b,
    MathOperation.DIVIDE:lambda term_a, term_b: term_a / term_b,
    MathOperation.POWER:lambda term_a, term_b: term_a ** term_b,
    MathOperation.MODULUS:lambda term_a, term_b: term_a % term_b,
    MathOperation.CARTESIAN_DISTANCE:lambda term_a, term_b: term_a.distance_to(term_b),
    MathOperation.ANGULAR_DISTANCE:lambda term_a, term_b: term_a.distance_to(term_b),
}

class Math(WiscBase):
    '''
    Class for defining mathematical operations
    '''

    keys = [set(('term_a','term_b','operation'))]

    def __init__(self,term_a,term_b=None,operation=None):
        self.term_a = term_a
        self.term_b = term_b
        self.operation = operation

    @classmethod
    def load(cls, serialized: dict, context: list):
        '''
        TODO: handle whatever context-grabbing implementation we use here for
        non-math terms.
        '''
        return Math(term_a=parse([Math],serialized['term_a']),
                    term_b=parse([Math],serialized['term_b']),
                    operation=MathOperation.load(serialized['operation']))

    @property
    def serialized(self):
        return {'term_a':self.term_a.serialized,
                'term_b':self.term_b.serialized,
                'operation':self.operation.serialized
                }

    def execute(self,context):
        lhs = Math.resolve(self.term_a, context)
        rhs = Math.resolve(self.term_b, context)
        return EXECUTION[self.operation](lhs, rhs)

    @classmethod
    def resolve(self,term,context):
        if isinstance(term,(int,float)):
            return term
        elif isinstance(term,Math):
            return term.execute(context)
        elif isinstance(term,WiscBase):
            return context.get(term)

    def __add__(self,other):
        if isinstance(other,(WiscBase,int,float)):
            return Math(self,other,MathOperation.ADD)
        else:
            return None

    def __sub__(self,other):
        if isinstance(other,(WiscBase,int,float)):
            return Math(self,other,MathOperation.SUBTRACT)
        else:
            return None

    def __mul__(self,other):
        if isinstance(other,(WiscBase,int,float)):
            return Math(self,other,MathOperation.MULTIPLY)
        else:
            return None

    def __truediv__(self,other):
        if isinstance(other,(WiscBase,int,float)):
            return Math(self,other,MathOperation.DIVIDE)
        else:
            return None

    def __mod__(self,other):
        if isinstance(other,(WiscBase,int,float)):
            return Math(self,other,MathOperation.MODULUS)
        else:
            return None

    def __lt__(self,other):
        if isinstance(other,(WiscBase,int,float)):
            return Math(self,other,PropertyOperation.LESS_THAN)
        else:
            return None

    def __le__(self,other):
        if isinstance(other,(WiscBase,int,float)):
            return Math(self,other,PropertyOperation.LESS_THAN_OR_EQUALS)
        else:
            return None

    def __gt__(self,other):
        if isinstance(other,(WiscBase,int,float)):
            return Math(self,other,PropertyOperation.GREATER_THAN)
        else:
            return None

    def __ge__(self,other):
        if isinstance(other,(WiscBase,int,float)):
            return Math(self,other,PropertyOperation.GREATER_THAN_OR_EQUALS)
        else:
            return None

    def __eq__(self,other):
        if isinstance(other,(WiscBase,int,float)):
            return Math(self,other,PropertyOperation.EQUALS)
        else:
            return None

'''
b = Math(2)
c = Math(3)
a = Math(b, c, MathOperation.ADD)
print(a.exec()) # 5
'''
